"""Failure controls for evidence corruption and unproved reading coverage."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from prepare_packets import B
from project_prior_sol import literal_whitespace_span, project
from validate_output import command_chunk_trim_loss, command_chunk_utf8_wrap_loss, contains_exact_chunk, native_read_bom_loss, validate


class EvidenceValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.packet, self.output, self.receipts = [root / n for n in ('document_test', 'output', 'receipts')]
        for p in (self.packet, self.output, self.receipts, self.packet / 'chunks'):
            p.mkdir(exist_ok=True)
        text = 'We retest the original claim.\nThe effect α\u00a0failed.\n'
        raw = text.encode()
        self.source_hash = hashlib.sha256(raw).hexdigest()
        (self.packet / 'article.txt').write_bytes(raw)
        (self.packet / 'coding_schema.json').write_bytes((B / 'coding_schema.json').read_bytes())
        meta = dict(work_key=self.packet.name, status='done', evidence_level='full_text',
                    source_url=None, retrieved_at=None, text_sha256=self.source_hash, parser=None)
        self.write(self.packet / 'metadata.json', meta)
        quote = text[:28]
        self.coding = dict(meta, record_type='unclear', record_type_quote=quote,
                           study_status='completed', targets=[], reasoning='Test fixture.')
        self.write(self.output / 'coding.json', self.coding)
        self.proof = dict(quote=quote, character_start=0, character_end=len(quote),
                          utf8_start=0, utf8_end=len(quote.encode()), source_sha256=self.source_hash,
                          quote_sha256=hashlib.sha256(quote.encode()).hexdigest(), field_path='record_type_quote')
        for filename in ('quote_spans.json', 'evidence_map.json'):
            self.write(self.output / filename, dict(text_sha256=self.source_hash, spans=[self.proof]))
        self.write(self.output / 'reading_manifest.json', dict(text_sha256=self.source_hash,
                   model_visible_character_ranges=[[0, len(text)]], full_source_read=True,
                   untruncated_tool_evidence=['fixture receipt']))
        self.write(self.packet / 'chunks.json', dict(chunks=[dict(file='chunks/one.txt', character_start=0,
                   character_end=len(text), sha256=self.source_hash)]))
        (self.packet / 'chunks/one.txt').write_bytes(raw)
        self.receipt = dict(type='command_execution', textTruncated=False, threadId='fixture',
                            itemId='fixture', position=1,
                            text='$ cat document_test/chunks/one.txt\n=====BEGIN\n' + text + '=====END')
        self.write(self.receipts / 'item_1.json', self.receipt)
        self.expected_inputs = {p.relative_to(self.packet).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in self.packet.rglob('*') if p.is_file()}

    @staticmethod
    def write(path, value):
        path.write_text(json.dumps(value))

    def run_validation(self):
        return validate(self.packet, self.output, self.receipts, self.expected_inputs)

    def test_valid_is_only_mechanical(self):
        result = self.run_validation()
        self.assertFalse(result['automatic_scientific_acceptance'])
        self.assertTrue(result['full_model_visible_reading_receipts_verified'])

    def bound_relative_receipt(self):
        thread = 'thread:fixture'
        return dict(self.receipt, threadId=thread, sourceThreadId=thread,
                    text="$ /bin/bash -lc 'cat chunks/one.txt'\n" + (self.packet / 'chunks/one.txt').read_text(),
                    parent_single_packet_binding=dict(packet_ids=[self.packet.name],
                        packet_path=str(self.packet.resolve()), source_sha256=self.source_hash,
                        taskId='node:fixture', childThreadId=thread, prompt_sha256='a' * 64))

    def test_bound_relative_chunk_has_full_mechanical_coverage(self):
        self.write(self.receipts / 'item_1.json', self.bound_relative_receipt())
        self.assertTrue(self.run_validation()['full_model_visible_reading_receipts_verified'])

    def test_relative_chunk_without_parent_binding_is_rejected(self):
        item = self.bound_relative_receipt(); item.pop('parent_single_packet_binding')
        self.write(self.receipts / 'item_1.json', item)
        with self.assertRaises(ValueError): self.run_validation()

    def test_relative_binding_cannot_cross_packets_or_task_threads(self):
        for changes in [dict(packet_ids=['another']), dict(packet_ids=[self.packet.name, 'another']),
                        dict(packet_path='/elsewhere'), dict(childThreadId='thread:other'),
                        dict(taskId='node:other'), dict(source_sha256='0' * 64), dict(prompt_sha256='')]:
            with self.subTest(changes=changes):
                item = self.bound_relative_receipt(); item['parent_single_packet_binding'].update(changes)
                self.write(self.receipts / 'item_1.json', item)
                with self.assertRaises(ValueError): self.run_validation()

    def test_relative_cat_cannot_hide_missing_or_changed_interior_source(self):
        for transform in [lambda t: t[3:], lambda t: t.replace('failed', 'passed'),
                          lambda t: t.replace('\u00a0', ' ')]:
            item = self.bound_relative_receipt(); command, _, body = item['text'].partition('\n')
            item['text'] = command + '\n' + transform(body)
            self.write(self.receipts / 'item_1.json', item)
            with self.assertRaises(ValueError): self.run_validation()

    def test_relative_cat_rejects_extra_shell_operations_and_wrong_file(self):
        for command in ["$ /bin/bash -lc 'cat chunks/one.txt; cat other.txt'",
                        "$ /bin/bash -lc 'cat chunks/two.txt'", "$ cat chunks/one.txt"]:
            item = self.bound_relative_receipt(); item['text'] = command + '\n' + (self.packet / 'chunks/one.txt').read_text()
            self.write(self.receipts / 'item_1.json', item)
            with self.assertRaises(ValueError): self.run_validation()

    def test_relative_cat_still_rejects_truncated_native_item(self):
        item = self.bound_relative_receipt(); item['textTruncated'] = True
        self.write(self.receipts / 'item_1.json', item)
        with self.assertRaises(ValueError): self.run_validation()

    def test_named_reading_range_still_requires_actual_complete_receipts(self):
        path=self.output/'reading_manifest.json'
        data=json.loads(path.read_text());n=len((self.packet/'article.txt').read_text())
        data['model_visible_character_ranges']=[dict(character_start=0,character_end=n)]
        self.write(path,data)
        self.assertTrue(self.run_validation()['full_model_visible_reading_receipts_verified'])
        self.receipt['text']=self.receipt['text'][:40]
        self.write(self.receipts/'item_1.json',self.receipt)
        with self.assertRaises(ValueError):self.run_validation()

    def test_named_reading_range_cannot_hide_unknown_fields_or_missing_coverage(self):
        path=self.output/'reading_manifest.json';data=json.loads(path.read_text())
        for interval in [dict(character_start=0,character_end=2),
                         dict(character_start=0,character_end=2,quote='fabricated')]:
            with self.subTest(interval=interval):
                data['model_visible_character_ranges']=[interval];self.write(path,data)
                with self.assertRaises(AssertionError):self.run_validation()

    def test_explicit_unicode_character_offset_names_keep_literal_checks(self):
        proof=dict(self.proof)
        proof['unicode_char_start']=proof.pop('character_start')
        proof['unicode_char_end']=proof.pop('character_end')
        self.write(self.output/'quote_spans.json',dict(source_sha256=self.source_hash,quote_spans=[proof]))
        self.assertEqual(self.run_validation()['span_map_proofs'],1)

    def test_conflicting_character_offset_alias_cannot_be_ignored(self):
        proof=dict(self.proof,unicode_char_start=1)
        self.write(self.output/'quote_spans.json',dict(source_sha256=self.source_hash,quote_spans=[proof]))
        with self.assertRaisesRegex(ValueError,'conflicting character offset aliases'):
            self.run_validation()

    def test_report_boundary_is_not_counted_as_a_quote_proof(self):
        data = dict(text_sha256=self.source_hash, spans=[self.proof], report_boundaries=[
            dict(report='One report', character_start=0, character_end=28, target_indices=[])])
        self.write(self.output / 'evidence_map.json', data)
        self.assertEqual(self.run_validation()['evidence_map_proofs'], 1)

    def test_reports_envelope_retains_boundary_checks_without_counting_proofs(self):
        self.write(self.output/'evidence_map.json',dict(text_sha256=self.source_hash,
                   spans=[self.proof],reports=[dict(report='One report',target_indices=[0],
                   character_start=0,character_end=28)]))
        self.assertEqual(self.run_validation()['evidence_map_proofs'],1)

    def test_reports_envelope_cannot_hide_quoted_content(self):
        self.write(self.output/'evidence_map.json',dict(text_sha256=self.source_hash,
                   spans=[self.proof],reports=[dict(report='One report',target_indices=[0],
                   character_start=0,character_end=28,quote='fabricated')]))
        with self.assertRaisesRegex(ValueError,'metadata cannot substitute'):
            self.run_validation()

    def test_named_section_boundaries_remain_metadata(self):
        for key in ['figure_captions_boundary','references_section_boundary']:
            with self.subTest(key=key):
                self.write(self.output/'evidence_map.json',dict(text_sha256=self.source_hash,
                           spans=[self.proof],**{key:dict(report='Section labels',character_start=0,character_end=28)}))
                self.assertEqual(self.run_validation()['evidence_map_proofs'],1)

    def test_named_section_boundary_cannot_hide_quoted_content(self):
        for key in ['figure_captions_boundary','references_section_boundary']:
            with self.subTest(key=key):
                self.write(self.output/'evidence_map.json',dict(text_sha256=self.source_hash,
                           spans=[self.proof],**{key:dict(report='Section labels',character_start=0,
                           character_end=28,quote='fabricated')}))
                with self.assertRaisesRegex(ValueError,'metadata cannot substitute'):
                    self.run_validation()

    def test_report_boundary_cannot_claim_a_quote_without_proof(self):
        data = dict(text_sha256=self.source_hash, spans=[self.proof], report_boundaries=[
            dict(report='One report', character_start=0, character_end=28, target_indices=[], quote='fabricated')])
        self.write(self.output / 'evidence_map.json', data)
        with self.assertRaises(ValueError):
            self.run_validation()

    def test_report_boundary_without_target_assignment_is_not_a_proof(self):
        data = dict(text_sha256=self.source_hash, spans=[self.proof], report_boundaries=[
            dict(report='Main paper', character_start=0, character_end=28)])
        self.write(self.output / 'evidence_map.json', data)
        self.assertEqual(self.run_validation()['evidence_map_proofs'], 1)

    def test_described_report_boundary_is_metadata_not_a_quote_proof(self):
        data = dict(text_sha256=self.source_hash, spans=[self.proof], report_boundaries=[
            dict(report_id='main_report', title='One report', structure='Introduction then analysis',
                 character_start=0, character_end=28)])
        self.write(self.output / 'evidence_map.json', data)
        self.assertEqual(self.run_validation()['evidence_map_proofs'], 1)

    def test_report_label_without_source_range_is_not_a_proof(self):
        self.write(self.output/'evidence_map.json',dict(text_sha256=self.source_hash,
                   spans=[self.proof],report_boundaries=[dict(report='One experiment',target_indices=[0])]))
        self.assertEqual(self.run_validation()['evidence_map_proofs'],1)

    def test_report_boundary_cannot_claim_only_one_offset(self):
        self.write(self.output/'evidence_map.json',dict(text_sha256=self.source_hash,
                   spans=[self.proof],report_boundaries=[dict(report='One experiment',character_start=0)]))
        with self.assertRaises(ValueError):self.run_validation()

    def test_described_boundary_cannot_claim_an_unproved_quote(self):
        boundary=dict(report_id='main_report',title='One report',structure='Analysis',
                      character_start=0,character_end=28,quote='fabricated')
        self.write(self.output/'evidence_map.json',dict(text_sha256=self.source_hash,
                   spans=[self.proof],report_boundaries=[boundary]))
        with self.assertRaises(ValueError):self.run_validation()

    def test_boundary_structure_cannot_hide_a_nested_quote_object(self):
        boundary=dict(report_id='main_report',title='One report',structure={'quote':'fabricated'},
                      character_start=0,character_end=28)
        self.write(self.output/'evidence_map.json',dict(text_sha256=self.source_hash,
                   spans=[self.proof],report_boundaries=[boundary]))
        with self.assertRaises(ValueError):self.run_validation()

    def test_optional_boundary_targets_must_still_be_a_list(self):
        data = dict(text_sha256=self.source_hash, spans=[self.proof], report_boundaries=[
            dict(report='Main paper', character_start=0, character_end=28, target_indices=None)])
        self.write(self.output / 'evidence_map.json', data)
        with self.assertRaises(ValueError):
            self.run_validation()

    def test_report_boundary_must_be_within_the_source(self):
        data = dict(text_sha256=self.source_hash, spans=[self.proof], report_boundaries=[
            dict(report='One report', character_start=0, character_end=9999, target_indices=[])])
        self.write(self.output / 'evidence_map.json', data)
        with self.assertRaises(ValueError):
            self.run_validation()

    def test_unlabelled_missing_quote_is_still_rejected(self):
        data = dict(text_sha256=self.source_hash, spans=[self.proof], claims=[
            dict(character_start=0, character_end=28)])
        self.write(self.output / 'evidence_map.json', data)
        with self.assertRaises(ValueError):
            self.run_validation()

    def test_declared_fold_preserves_unicode_and_records_insertions(self):
        source = '\u03b1' * 1000 + 'B' * 2000 + 'end '
        rendered = '\u03b1' * 1000 + '\n' + 'B' * 2000 + '\nend'
        self.assertEqual(command_chunk_utf8_wrap_loss('$ cat chunks/one.txt | fold -w 2000', rendered, source, 'one.txt'),
                         (1, 2))

    def test_transport_wrap_cannot_hide_a_changed_source_character(self):
        source = '\u03b1' * 1000 + 'B' * 2000 + 'end '
        rendered = '\u03b1' * 1000 + '\n' + 'B' * 1999 + 'C\nend'
        self.assertIsNone(command_chunk_utf8_wrap_loss('$ cat chunks/one.txt | fold -w 2000', rendered, source, 'one.txt'))

    def test_transport_wrap_does_not_accept_arbitrary_newline_normalization(self):
        source = '\u03b1' * 1000 + 'B' * 2000 + 'end '
        rendered = '\u03b1' * 999 + '\n\u03b1' + 'B' * 2000 + '\nend'
        self.assertIsNone(command_chunk_utf8_wrap_loss('$ cat chunks/one.txt | fold -w 2000', rendered, source, 'one.txt'))

    def test_fold_rendering_requires_the_declared_fold_command(self):
        source = '\u03b1' * 1000 + 'B' * 2000 + 'end '
        rendered = '\u03b1' * 1000 + '\n' + 'B' * 2000 + '\nend'
        self.assertIsNone(command_chunk_utf8_wrap_loss('$ cat chunks/one.txt', rendered, source, 'one.txt'))

    def test_literal_proof_alias_still_requires_the_exact_source_span(self):
        proof = dict(self.proof)
        proof['literal_proof'] = proof.pop('quote')
        self.write(self.output / 'evidence_map.json', dict(text_sha256=self.source_hash, spans=[proof]))
        self.assertEqual(self.run_validation()['evidence_map_proofs'], 1)

    def test_literal_proof_alias_cannot_pass_changed_words(self):
        proof = dict(self.proof)
        proof['literal_proof'] = proof.pop('quote').replace('original', 'invented')
        self.write(self.output / 'evidence_map.json', dict(text_sha256=self.source_hash, spans=[proof]))
        with self.assertRaisesRegex(ValueError, 'character mismatch'):
            self.run_validation()

    def test_literal_proof_alias_cannot_hide_a_conflicting_quote(self):
        proof = dict(self.proof, literal_proof='A different claim.')
        self.write(self.output / 'evidence_map.json', dict(text_sha256=self.source_hash, spans=[proof]))
        with self.assertRaisesRegex(ValueError, 'conflicting literal quote aliases'):
            self.run_validation()

    def test_claimed_reading_without_tool_output_rejected(self):
        (self.receipts / 'item_1.json').unlink()
        with self.assertRaises(ValueError): self.run_validation()

    def test_truncated_tool_output_rejected(self):
        self.receipt['textTruncated'] = True
        self.write(self.receipts / 'item_1.json', self.receipt)
        with self.assertRaises(ValueError): self.run_validation()

    def native_read_receipt(self, content):
        path = str((self.packet / 'chunks/one.txt').resolve())
        self.receipt.update(type='dynamic_tool', text=json.dumps(dict(toolName='Read',
                            input=dict(file_path=path), output=dict(file=dict(filePath=path,
                            startLine=1, numLines=3, totalLines=3, content=content)))))
        self.write(self.receipts / 'item_1.json', self.receipt)

    def test_native_read_exact_content_accepted(self):
        self.native_read_receipt((self.packet / 'article.txt').read_bytes().decode())
        self.assertTrue(self.run_validation()['full_model_visible_reading_receipts_verified'])

    def test_native_read_missing_content_rejected_despite_line_counts(self):
        self.native_read_receipt('We retest the original claim.')
        with self.assertRaises(ValueError): self.run_validation()

    def test_native_read_single_utf8_signature_is_only_allowed_omission(self):
        path = self.packet / 'chunks/one.txt'
        self.native_read_receipt('Complete α text.\n')
        raw = '\ufeffComplete α text.\n'.encode()
        self.assertEqual(native_read_bom_loss(self.receipt, path, raw), 1)
        self.assertTrue(contains_exact_chunk(self.receipt, self.packet, path, raw))
        self.assertEqual(native_read_bom_loss(self.receipt, path, raw[3:]), 0)

    def test_native_read_bom_rule_rejects_source_edits_and_other_whitespace_loss(self):
        path = self.packet / 'chunks/one.txt'
        raw = '\ufeff\nComplete α text.\n'.encode()
        for shown in ('Complete α text.\n', '\nComplete text.\n', '\nComplete α text.', '\nComplete α text. extra\n'):
            self.native_read_receipt(shown)
            with self.subTest(shown=shown):
                self.assertIsNone(native_read_bom_loss(self.receipt, path, raw))

    def test_native_read_bom_rule_cannot_strip_multiple_or_interior_markers(self):
        path = self.packet / 'chunks/one.txt'
        self.native_read_receipt('Complete text.\n')
        for text in ('\ufeff\ufeffComplete text.\n', 'Complete\ufeff text.\n'):
            with self.subTest(text=text):
                self.assertIsNone(native_read_bom_loss(self.receipt, path, text.encode()))

    def test_native_read_bom_still_requires_exact_paths_and_complete_line_range(self):
        path = self.packet / 'chunks/one.txt'
        raw = '\ufeffComplete text.\n'.encode()
        for mutation in ('input-path', 'output-path', 'start-line', 'partial-lines'):
            self.native_read_receipt('Complete text.\n')
            call = json.loads(self.receipt['text'])
            if mutation == 'input-path':
                call['input']['file_path'] = '/other/source'
            elif mutation == 'output-path':
                call['output']['file']['filePath'] = '/other/source'
            elif mutation == 'start-line':
                call['output']['file']['startLine'] = 2
            else:
                call['output']['file']['numLines'] = 2
            self.receipt['text'] = json.dumps(call)
            with self.subTest(mutation=mutation):
                self.assertIsNone(native_read_bom_loss(self.receipt, path, raw))

    def test_native_read_bom_does_not_override_truncation(self):
        self.native_read_receipt('Complete text.\n')
        self.receipt['textTruncated'] = True
        self.assertIsNone(native_read_bom_loss(self.receipt, self.packet / 'chunks/one.txt',
                                              '\ufeffComplete text.\n'.encode()))

    def test_native_read_bom_receipt_records_loss_without_changing_frozen_bytes(self):
        raw = b'\xef\xbb\xbf' + (self.packet / 'article.txt').read_bytes()
        source_hash = hashlib.sha256(raw).hexdigest()
        for path in (self.packet / 'article.txt', self.packet / 'chunks/one.txt'):
            path.write_bytes(raw)
        self.coding['text_sha256'] = source_hash
        meta = json.loads((self.packet / 'metadata.json').read_text())
        meta['text_sha256'] = source_hash
        self.write(self.packet / 'metadata.json', meta)
        self.write(self.output / 'coding.json', self.coding)
        self.proof.update(character_start=1, character_end=1 + len(self.proof['quote']),
                          utf8_start=3, utf8_end=3 + len(self.proof['quote'].encode()), source_sha256=source_hash)
        for name in ('quote_spans.json', 'evidence_map.json'):
            self.write(self.output / name, dict(text_sha256=source_hash, spans=[self.proof]))
        self.write(self.output / 'reading_manifest.json', dict(text_sha256=source_hash,
                   model_visible_character_ranges=[[0, len(raw.decode())]], full_source_read=True,
                   untruncated_tool_evidence=['fixture receipt']))
        self.write(self.packet / 'chunks.json', dict(chunks=[dict(file='chunks/one.txt', character_start=0,
                   character_end=len(raw.decode()), sha256=source_hash)]))
        self.expected_inputs = {p.relative_to(self.packet).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in self.packet.rglob('*') if p.is_file()}
        self.native_read_receipt(raw[3:].decode())
        result = self.run_validation()
        self.assertEqual(result['reading_receipts'][0]['leading_whitespace_or_bom_not_preserved_by_timeline'], 1)
        self.assertEqual((self.packet / 'article.txt').read_bytes(), raw)

    def test_plain_cat_exact_output_accepted(self):
        text = (self.packet / 'article.txt').read_bytes().decode()
        self.receipt['text'] = '$ cat document_test/chunks/one.txt\n' + text
        self.write(self.receipts / 'item_1.json', self.receipt)
        self.assertTrue(self.run_validation()['full_model_visible_reading_receipts_verified'])

    def test_timeline_trailing_whitespace_crop_recorded(self):
        text = (self.packet / 'article.txt').read_bytes().decode()
        self.receipt['text'] = '$ cat document_test/chunks/one.txt\n' + text.rstrip()
        self.write(self.receipts / 'item_1.json', self.receipt)
        result = self.run_validation()
        self.assertEqual(result['reading_receipts'][0]['trailing_whitespace_not_preserved_by_timeline'], 1)

    def test_cat_losing_substantive_character_rejected(self):
        text = (self.packet / 'article.txt').read_bytes().decode()
        self.receipt['text'] = '$ cat document_test/chunks/one.txt\n' + text.rstrip()[:-1]
        self.write(self.receipts / 'item_1.json', self.receipt)
        with self.assertRaises(ValueError): self.run_validation()

    def test_json_pointer_quote_path_accepted(self):
        proof = dict(self.proof, field_path='/record_type_quote')
        self.write(self.output / 'quote_spans.json', dict(text_sha256=self.source_hash, spans=[proof]))
        self.assertEqual(self.run_validation()['coding_quote_fields'], 1)

    def test_quote_crossing_original_source_boundary_rejected(self):
        text = (self.packet / 'article.txt').read_text()
        blocks = []
        for a, z in [(0, 10), (10, len(text))]:
            blocks.append(dict(character_start=a, character_end=z,
                               source_raw_sha256=hashlib.sha256(text[a:z].encode()).hexdigest()))
        self.write(self.packet / 'source_blocks.json', dict(text_sha256=self.source_hash, blocks=blocks))
        self.expected_inputs['source_blocks.json'] = hashlib.sha256((self.packet / 'source_blocks.json').read_bytes()).hexdigest()
        with self.assertRaises(ValueError): self.run_validation()

    def test_incomplete_reading_rejected(self):
        p = self.output / 'reading_manifest.json'
        m = json.loads(p.read_text()); m['model_visible_character_ranges'] = [[1, 48]]
        self.write(p, m)
        with self.assertRaises(AssertionError): self.run_validation()

    def test_false_byte_offset_rejected(self):
        proof = dict(self.proof, utf8_end=999)
        self.write(self.output / 'evidence_map.json', dict(text_sha256=self.source_hash, spans=[proof]))
        with self.assertRaises(ValueError): self.run_validation()

    def test_other_source_proof_rejected(self):
        proof = dict(self.proof, source_sha256='0' * 64)
        self.write(self.output / 'evidence_map.json', dict(text_sha256=self.source_hash, spans=[proof]))
        with self.assertRaises(ValueError): self.run_validation()

    def test_per_proof_source_hashes_establish_map_without_root_hash(self):
        self.write(self.output / 'evidence_map.json', dict(spans=[self.proof]))
        self.assertEqual(self.run_validation()['evidence_map_proofs'], 1)

    def test_map_without_root_or_proof_source_hash_rejected(self):
        proof = dict(self.proof)
        del proof['source_sha256']
        self.write(self.output / 'evidence_map.json', dict(spans=[proof]))
        with self.assertRaises(ValueError): self.run_validation()

    def test_empty_evidence_placeholder_is_retained_as_unproved_not_a_proof(self):
        placeholder = dict(self.proof, quote='', character_start=None, character_end=None,
                           utf8_start=None, utf8_end=None, quote_sha256=None, work='Unproved exclusion')
        self.write(self.output / 'evidence_map.json', dict(text_sha256=self.source_hash,
                   spans=[self.proof], excluded_candidates=[placeholder]))
        result = self.run_validation()
        self.assertEqual(result['evidence_map_proofs'], 1)
        self.assertEqual(len(result['unproved_evidence_entries']), 1)
        self.assertIn('not_accepted', result['unproved_evidence_entries'][0]['status'])

    def test_nonempty_quote_with_null_coordinates_still_rejected(self):
        proof = dict(self.proof, character_start=None, character_end=None, utf8_start=None, utf8_end=None)
        self.write(self.output / 'evidence_map.json', dict(text_sha256=self.source_hash, spans=[proof]))
        with self.assertRaises(ValueError): self.run_validation()

    def test_empty_placeholder_with_a_claimed_quote_hash_rejected(self):
        proof = dict(self.proof, quote='', character_start=None, character_end=None,
                     utf8_start=None, utf8_end=None)
        self.write(self.output / 'evidence_map.json', dict(text_sha256=self.source_hash, spans=[proof]))
        with self.assertRaises(ValueError): self.run_validation()

    def test_semantic_schema_extra_rejected(self):
        self.coding['safe'] = True
        self.write(self.output / 'coding.json', self.coding)
        with self.assertRaises(Exception): self.run_validation()

    def test_changed_source_rejected(self):
        (self.packet / 'article.txt').write_text('Different evidence.')
        with self.assertRaises(ValueError): self.run_validation()

    def test_matching_forged_packet_and_result_metadata_rejected(self):
        metadata = json.loads((self.packet / 'metadata.json').read_text())
        metadata['source_url'] = 'https://example.invalid/other-version'
        self.write(self.packet / 'metadata.json', metadata)
        self.coding['source_url'] = metadata['source_url']
        self.write(self.output / 'coding.json', self.coding)
        with self.assertRaises(ValueError): self.run_validation()

    def test_changed_word_cannot_be_transcribed(self):
        with self.assertRaises(ValueError):
            literal_whitespace_span('The effect failed.', 'The effect succeeded.')

    def test_ambiguous_whitespace_match_rejected(self):
        with self.assertRaises(ValueError):
            literal_whitespace_span('a b a b', 'a\nb')

    def test_whitespace_projection_preserves_labels_and_original(self):
        self.coding['record_type_quote'] = 'The effect α failed.'
        original = copy.deepcopy(self.coding)
        projected, ledger = project(self.packet, self.coding)
        self.assertEqual(self.coding, original)
        self.assertEqual(projected['record_type'], original['record_type'])
        self.assertEqual(projected['record_type_quote'], 'The effect α\u00a0failed.')
        self.assertFalse(ledger['scientific_labels_modified'])
        self.assertEqual(len(ledger['quote_transcriptions']), 1)

    def test_provenance_cannot_hide_scientific_change(self):
        self.coding['parent_provenance_completion'] = dict(filled_fields=['outcome'], original_values={'outcome': 'failed'})
        with self.assertRaises(ValueError): project(self.packet, self.coding)

    def test_opaque_parser_redaction_is_logged_without_changing_old_coding(self):
        self.coding['parser'] = 'parent-supplied cached text; cache helper unspecified'
        original = copy.deepcopy(self.coding)
        projected, ledger = project(self.packet, self.coding)
        self.assertIsNone(projected['parser'])
        self.assertEqual(self.coding, original)
        self.assertEqual(ledger['excluded_technical_metadata']['opaque_packet_parser_redaction']['original_value'], original['parser'])
        self.assertFalse(ledger['scientific_labels_modified'])

    def test_parser_redaction_does_not_allow_other_metadata_changes(self):
        self.coding['parser'] = 'parent-supplied cached text'
        self.coding['source_url'] = 'https://example.invalid/different-source'
        with self.assertRaises(AssertionError): project(self.packet, self.coding)

    def test_unrelated_parser_mismatch_is_not_silently_replaced(self):
        self.coding['parser'] = 'pdftotext'
        with self.assertRaises(AssertionError): project(self.packet, self.coding)

    def test_terminal_bom_and_leading_blank_lines_are_recorded_as_trivia(self):
        source = (self.packet / 'article.txt').read_text()
        raw = ('\ufeff\n\n' + source).encode()
        command = f'$ cd {self.packet} && cat chunks/one.txt; echo END'
        item = dict(self.receipt, text=command + '\n' + source + 'END')
        self.assertTrue(contains_exact_chunk(item, self.packet, self.packet / 'chunks/one.txt', raw))
        self.assertEqual(command_chunk_trim_loss(command, source + 'END', raw.decode(), 'one.txt'), (3, 0))

    def test_terminal_trivia_exception_cannot_hide_missing_source_words(self):
        source = (self.packet / 'article.txt').read_text()
        command = f'$ cd {self.packet} && cat chunks/one.txt; echo END'
        item = dict(self.receipt, text=command + '\n' + source[3:] + 'END')
        self.assertFalse(contains_exact_chunk(item, self.packet, self.packet / 'chunks/one.txt',
                                             ('\ufeff\n\n' + source).encode()))

    def test_terminal_trivia_exception_cannot_normalize_interior_whitespace(self):
        source = (self.packet / 'article.txt').read_text()
        command = f'$ cd {self.packet} && cat chunks/one.txt; echo END'
        item = dict(self.receipt, text=command + '\n' + source.replace('\u00a0', ' ') + 'END')
        self.assertFalse(contains_exact_chunk(item, self.packet, self.packet / 'chunks/one.txt',
                                             ('\ufeff\n\n' + source).encode()))


if __name__ == '__main__':
    unittest.main()
