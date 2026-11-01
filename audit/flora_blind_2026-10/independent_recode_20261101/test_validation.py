"""Failure controls for evidence corruption and unproved reading coverage."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from prepare_packets import B
from project_prior_sol import literal_whitespace_span, project
from validate_output import validate


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

    @staticmethod
    def write(path, value):
        path.write_text(json.dumps(value))

    def run_validation(self):
        return validate(self.packet, self.output, self.receipts)

    def test_valid_is_only_mechanical(self):
        result = self.run_validation()
        self.assertFalse(result['automatic_scientific_acceptance'])
        self.assertTrue(result['full_model_visible_reading_receipts_verified'])

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

    def test_plain_cat_exact_output_accepted(self):
        text = (self.packet / 'article.txt').read_bytes().decode()
        self.receipt['text'] = '$ cat document_test/chunks/one.txt\n' + text
        self.write(self.receipts / 'item_1.json', self.receipt)
        self.assertTrue(self.run_validation()['full_model_visible_reading_receipts_verified'])

    def test_json_pointer_quote_path_accepted(self):
        proof = dict(self.proof, field_path='/record_type_quote')
        self.write(self.output / 'quote_spans.json', dict(text_sha256=self.source_hash, spans=[proof]))
        self.assertEqual(self.run_validation()['coding_quote_fields'], 1)

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

    def test_semantic_schema_extra_rejected(self):
        self.coding['safe'] = True
        self.write(self.output / 'coding.json', self.coding)
        with self.assertRaises(Exception): self.run_validation()

    def test_changed_source_rejected(self):
        (self.packet / 'article.txt').write_text('Different evidence.')
        with self.assertRaises(AssertionError): self.run_validation()

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


if __name__ == '__main__':
    unittest.main()
