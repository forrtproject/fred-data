import csv
import importlib.util
import json
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('compare', Path(__file__).with_name('compare.py'))
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with c.INPUT.open(encoding='utf-8-sig') as f:
            cls.rows = list(csv.DictReader(f))

    def test_replication(self):
        r = next(r for r in self.rows if r['type'] == 'replication')
        a = c.adapt_row(r)
        self.assertEqual(a['outcome'], r['outcome'])
        self.assertEqual(a['authors_o'].split('; ')[0], json.loads(r['author_o'])[0]['family'])

    def test_reproduction(self):
        for r in self.rows:
            if r['type'] == 'reproduction':
                a = c.adapt_row(r)
                self.assertNotEqual(a['outcome_computation'], 'unverified')
                self.assertNotEqual(a['outcome_robustness'], 'unverified')
        a = c.adapt_row({'type': 'reproduction', 'outcome': 'computation not checked, robustness not checked'})
        self.assertEqual((a['outcome_computation'], a['outcome_robustness']), ('not checked', 'not checked'))
        self.assertEqual(c.adapt_row({'type': 'replication', 'outcome': 'NA'})['outcome'], 'unverified')
        self.assertEqual(c.adapt_row({'type': 'reproduction', 'outcome': 'surprise'})['outcome_computation'], 'unverified')

    def test_missing_doi(self):
        r = next(r for r in self.rows if not c.clean_doi(r['doi_o']))
        self.assertEqual(c.clean_doi(c.adapt_row(r)['doi_o']), '')
        self.assertEqual(c.clean_doi('HTTPS://DOI.ORG/10.123/ABC'), '10.123/abc')

    def test_multi_original(self):
        by_work = {}
        for r in self.rows:
            by_work.setdefault(r['doi_r'], []).append(r)
        rows = next(rs for rs in by_work.values() if len(rs) > 1 and len({r['doi_o'] for r in rs}) > 1)
        adapted = [c.adapt_row(r) for r in rows]
        self.assertEqual(len(adapted), len(rows))
        self.assertGreater(len({r['doi_o'] for r in adapted}), 1)
        for r in adapted:
            self.assertIsInstance(r['authors_o'], str)



import hashlib
import subprocess
import sys
import tempfile
from unittest.mock import patch

TEXT = 'We replicate Smith 2000. The original result was confirmed. We used new data. Numbers reproduced. Robustness was not checked.'


def row(doi='10.1/a', title='The original experiment', author='Smith', yr='2000', typ='replication', outcome='successful'):
    return c.adapt_row({'doi_o': doi, 'title_o': title, 'author_o': json.dumps([{'family': author}]),
                        'year_o': yr, 'type': typ, 'outcome': outcome, 'doi_r': '10.2/r',
                        'source': 'fixture', 'outcome_quote': 'The original result was confirmed.'})


def target(doi='10.1/a', **kwargs):
    return {'doi': doi, 'title': 'The original experiment', 'authors': 'Smith, J.', 'year': '2000',
            'identified_by': 'citation', 'evidence_quote': 'We replicate Smith 2000.',
            'outcome': 'successful', 'outcome_quote': 'The original result was confirmed.',
            'outcome_quote_section': 'results', 'outcome_confident': False, **kwargs}


def coding(targets=None, **kwargs):
    return {'work_key': 'work', 'status': 'done', 'record_type': 'replication',
            'record_type_quote': 'We used new data.', 'study_status': 'completed',
            'targets': [target()] if targets is None else targets, 'reasoning': '',
            'evidence_level': 'full_text', 'source_url': 'https://example.org/paper',
            'retrieved_at': '2026-10-29', 'parser': 'fixture',
            'text_sha256': hashlib.sha256(TEXT.encode()).hexdigest(), **kwargs}


def compare(rows=None, code=None, error='', text=TEXT, decisions=None):
    rows = [row()] if rows is None else rows
    keys = [{'input_row_index': str(i), 'work_key': 'work', 'file_key': 'file'} for i in range(len(rows))]
    return c.compare_work(rows, keys, coding() if code is None else code, error, text, decisions or [])


def decision(field='outcome', **kwargs):
    return {'input_row_index': 0, 'field': field, 'method': 'argon', 'verdict': 'blind_right',
            'corrected_value': 'failed', 'quote': 'The original result was confirmed.',
            'location': 'results', 'reason': 'fixture adjudicator determination', **kwargs}


class PairingTests(unittest.TestCase):
    def test_exact_doi_reserved_first(self):
        rows = [row('10.1/a'), row('')]
        ts = [target(''), target('10.1/a')]
        pairs, _, _ = c.pair_originals(rows, ts)
        self.assertIn((0, 1), [(i, j) for i, j, _, _ in pairs])
        self.assertEqual(len(pairs), 2)

    def test_global_cardinality_beats_greedy(self):
        grades = {(0, 0): ('title', .99), (0, 1): ('title', .7),
                  (1, 0): ('author_year', .4), (1, 1): ('different', 0)}
        rows = [dict(row(''), number=i) for i in range(2)]
        ts = [dict(target(''), number=j) for j in range(2)]
        with patch.object(c, 'original_grade', side_effect=lambda r, t: grades[r['number'], t['number']]):
            pairs, flags, _ = c.pair_originals(rows, ts)
        self.assertEqual({(i, j) for i, j, _, _ in pairs}, {(0, 1), (1, 0)})
        self.assertIn('competing_supported_matches', flags[0])

    def test_maximum_strength_among_equal_cardinality(self):
        grades = {(0, 0): ('title', .9), (0, 1): ('title', .7),
                  (1, 0): ('title', .6), (1, 1): ('title', .95)}
        rows = [dict(row(''), number=i) for i in range(2)]
        ts = [dict(target(''), number=j) for j in range(2)]
        with patch.object(c, 'original_grade', side_effect=lambda r, t: grades[r['number'], t['number']]):
            pairs, _, _ = c.pair_originals(rows, ts)
        self.assertEqual({(i, j) for i, j, _, _ in pairs}, {(0, 0), (1, 1)})

    def test_conflicting_dois_unverified(self):
        rs, _, _ = compare(code=coding([target('10.1/other')]))
        self.assertIn('conflicting_dois', rs[0]['pairing_flags'])
        self.assertFalse(rs[0]['identity_resolved'])
        self.assertEqual(rs[0]['outcome_grade'], 'unverified')
        self.assertEqual(rs[0]['original_final_verdict'], 'unverified')

    def test_siblings_and_duplicate_dois_flagged(self):
        pairs, flags, _ = c.pair_originals([row(''), row('', title='Different sibling paper')], [target('', title='')])
        self.assertTrue(any('same_author_year_siblings' in fs for fs in flags.values()))
        pairs, flags, _ = c.pair_originals([row(), row()], [target()])
        self.assertEqual(len(pairs), 1)
        self.assertTrue(all('competing_exact_doi' in fs for fs in flags.values()))

    def test_unmatched_and_missing_are_not_errors(self):
        rs, missing, ds = compare(code=coding([target('10.9/x', title='Unrelated effects', authors='Jones, A.', year='2010')]))
        self.assertEqual(rs[0]['original_grade'], 'unmatched')
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]['final_verdict'], 'unverified')
        self.assertTrue(all(rs[0][f + '_final_verdict'] == 'unverified' for f in c.FIELDS))


class EvidenceTests(unittest.TestCase):
    def test_presence_contiguous_and_all_parts(self):
        self.assertTrue(c.quote_present('The original result was confirmed.', TEXT))
        self.assertTrue(c.quote_present('Numbers reproduced. | Robustness was not checked.', TEXT))
        self.assertFalse(c.quote_present('We replicate Smith 2000. | Invented claim.', TEXT))
        self.assertFalse(c.quote_present('We replicate Smith 2000. Numbers reproduced.', TEXT))
        self.assertFalse(c.quote_present('', TEXT))
        self.assertFalse(c.quote_present('p < .05', 'p > .05'))
        self.assertFalse(c.quote_present('effect = 0.5', 'effect = -0.5'))
        self.assertTrue(c.quote_present('The ﬁnding was reproduced.', 'The finding was re-\nproduced.'))

    def test_agreement_low_confidence_and_prospective(self):
        rs, _, _ = compare(code=coding(study_status='prospective'))
        self.assertTrue(rs[0]['type_agree'])
        self.assertEqual(rs[0]['study_status'], 'prospective')
        self.assertFalse(rs[0]['confident'])
        self.assertEqual(rs[0]['resolution'], 'agree')

    def test_disagreement_never_proves_error(self):
        rs, _, ds = compare(code=coding([target(outcome='failed')]))
        self.assertEqual(rs[0]['outcome_grade'], 'different')
        self.assertEqual(rs[0]['outcome_final_verdict'], 'unverified')
        self.assertTrue(ds)

    def test_unknown_cannot_be_evaluated(self):
        rs, _, _ = compare(rows=[row(outcome='cannot_be_determined')], code=coding([target(outcome='cannot_be_determined')]))
        self.assertEqual(rs[0]['outcome_grade'], 'unverified')
        self.assertEqual(rs[0]['outcome_final_verdict'], 'unverified')

    def test_missing_identity_quote_blocks_agreement(self):
        rs, _, _ = compare(code=coding([target(evidence_quote='Made up quotation.')]))
        self.assertTrue(all(rs[0][f + '_final_verdict'] == 'unverified' for f in c.FIELDS))

    def test_failed_and_unattempted_all_unverified_even_adjudicated(self):
        for status in ('timeout', 'no_text', 'error', 'unattempted'):
            rs, _, _ = compare(error=status, decisions=[decision()])
            self.assertTrue(all(rs[0][f + '_final_verdict'] == 'unverified' for f in c.FIELDS))

    def test_valid_adjudication_and_reject_invalid_quote(self):
        for method in ('obvious', 'argon'):
            rs, _, _ = compare(code=coding([target(outcome='failed')]), decisions=[decision(method=method)])
            self.assertEqual(rs[0]['outcome_final_verdict'], 'error')
            self.assertEqual(rs[0]['resolution'], method)
        for bad in (decision(quote='Fake quote.'), decision(location=''), decision(reason=''),
                    decision(method='blind'), decision(corrected_value='unclear')):
            rs, _, _ = compare(code=coding([target(outcome='failed')]), decisions=[bad])
            self.assertEqual(rs[0]['outcome_final_verdict'], 'unverified')

    def test_duplicate_decisions_do_not_resolve(self):
        rs, _, _ = compare(code=coding([target(outcome='failed')]), decisions=[decision(), decision()])
        self.assertEqual(rs[0]['outcome_final_verdict'], 'unverified')

    def test_shipped_quote_is_checked_not_assumed(self):
        r = row()
        r['outcome_phrase'] = 'Imaginary quotation.'
        rs, _, _ = compare(rows=[r])
        self.assertFalse(rs[0]['shipped_quote_present'])

    def test_reproduction_independent_axes(self):
        r = row(typ='reproduction', outcome='computationally reproducible, robustness not checked')
        t = target(outcome='', outcome_computation='computationally reproducible',
                   outcome_computational_quote='Numbers reproduced.', outcome_robustness='cannot_be_determined',
                   outcome_robustness_quote='')
        rs, _, _ = compare(rows=[r], code=coding([t], record_type='reproduction'))
        self.assertEqual(rs[0]['outcome_computation_final_verdict'], 'correct')
        self.assertEqual(rs[0]['outcome_robustness_final_verdict'], 'unverified')
        self.assertEqual(rs[0]['outcome_final_verdict'], 'unverified')

    def test_adjudication_resolves_conflicting_identity(self):
        ds = [decision('original', target_index=0, corrected_value={'doi': '10.1/b'})]
        rs, _, _ = compare(code=coding([target('10.1/b')]), decisions=ds)
        self.assertTrue(rs[0]['identity_resolved'])
        self.assertEqual(rs[0]['original_final_verdict'], 'error')
        self.assertEqual(rs[0]['outcome_final_verdict'], 'correct')

    def test_original_adjudication_cannot_call_unchanged_doi_error(self):
        ds = [decision('original', corrected_value={'doi': 'https://doi.org/10.1/A'})]
        rs, _, _ = compare(decisions=ds)
        self.assertEqual(rs[0]['original_final_verdict'], 'correct')



class CLITests(unittest.TestCase):
    def test_all_rows_and_incremental_adjudication(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            for name in ('codings', 'adjudications', 'texts'):
                (root / name).mkdir()
            raw = row()
            raw['author_o'] = json.dumps([{'family': 'Smith'}])
            c.write_csv(root / 'input.csv', [raw, raw], list(raw))
            c.write_csv(root / 'manifest.csv', [
                {'input_row_index': 1, 'work_key': 'work2', 'file_key': 'second'},
                {'input_row_index': 0, 'work_key': 'work', 'file_key': 'first'}],
                ['input_row_index', 'work_key', 'file_key'])
            (root / 'coding_schema.json').write_bytes((c.ROOT / 'coding_schema.json').read_bytes())
            code = coding([target(outcome='failed')], elapsed_seconds=4.2)
            (root / 'codings' / 'first.json').write_text(json.dumps(code))
            (root / 'texts' / 'first.txt').write_text(TEXT)
            cmd = [sys.executable, str(Path(c.__file__)), '--input', str(root / 'input.csv'), '--audit-dir', str(root)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rs = c.read_csv(root / 'results.csv')
            self.assertEqual([r['input_row_index'] for r in rs], ['0', '1'])
            self.assertEqual(rs[0]['outcome_final_verdict'], 'unverified')
            self.assertEqual(rs[1]['coding_status'], 'unattempted')
            self.assertTrue(all(rs[1][f + '_final_verdict'] == 'unverified' for f in c.FIELDS))
            (root / 'adjudications' / 'first.json').write_text(json.dumps({'decisions': [decision()]}))
            c.run(root / 'input.csv', root)
            self.assertEqual(c.read_csv(root / 'results.csv')[0]['outcome_final_verdict'], 'error')
            report = (root / 'REPORT.md').read_text()
            self.assertIn('provisional', report)
            self.assertIn('1 / 1 (100.0%)', report)
            self.assertIn('50.0%–100.0%', report)
            self.assertIn('4.2 seconds', report)
            self.assertIn('https://doi.org/10.2/r', report)
            self.assertTrue((root / 'missing_rows.csv').exists())
            self.assertTrue(json.loads((root / 'disagreements.json').read_text())['provisional'])
            (root / 'codings' / 'first.json').write_text(json.dumps(coding(status='timeout')))
            code_failed, error_failed, text_failed = c.load_coding(root, 'first', 'work', json.loads((root / 'coding_schema.json').read_text()))
            self.assertEqual(error_failed, 'timeout')
            self.assertEqual(text_failed, TEXT)
            (root / 'codings' / 'first.json').write_text(json.dumps(code))
            # Hash mismatch blocks even valid previous adjudication.
            (root / 'texts' / 'first.txt').write_text('Changed text')
            c.run(root / 'input.csv', root)
            rs = c.read_csv(root / 'results.csv')
            self.assertTrue(all(rs[0][f + '_final_verdict'] == 'unverified' for f in c.FIELDS))

    def test_malformed_coding_and_schema_failure_are_unverified(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            (root / 'codings').mkdir()
            for name in ('coding_schema.json',):
                (root / name).write_bytes((c.ROOT / name).read_bytes())
            c.write_csv(root / 'input.csv', [row()], list(row()))
            c.write_csv(root / 'manifest.csv', [{'input_row_index': 0, 'work_key': 'work', 'file_key': 'file'}],
                        ['input_row_index', 'work_key', 'file_key'])
            for content in ('{bad', json.dumps(coding(evidence_level=['invalid']))):
                (root / 'codings' / 'file.json').write_text(content)
                c.run(root / 'input.csv', root)
                rs = c.read_csv(root / 'results.csv')
                self.assertTrue(all(rs[0][f + '_final_verdict'] == 'unverified' for f in c.FIELDS))

    def test_full_manifest_without_codings(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            for name in ('manifest.csv', 'run_manifest.json', 'coding_schema.json'):
                (root / name).write_bytes((c.ROOT / name).read_bytes())
            summary = c.run(c.INPUT, root)
            self.assertEqual(summary['rows'], 2818)
            self.assertEqual(summary['works'], 2344)
            rs = c.read_csv(root / 'results.csv')
            self.assertTrue(all(r[f + '_final_verdict'] == 'unverified' for r in rs for f in c.FIELDS))


if __name__ == '__main__':
    unittest.main()


class CitationSurnameTests(unittest.TestCase):
    def test_surname_first_initial_formats(self):
        for citation in ('Bryan CJ, Adams GS, Monin B', 'Bryan, C. J.; Adams, G. S.', 'Bryan C. J.', 'Bryan; Adams'):
            self.assertEqual(c.surname(citation), 'bryan')
        self.assertEqual(c.surname('van Dijk J. R., Smith A.'), 'vandijk')
        self.assertEqual(c.surname('van Dijk; Smith'), 'vandijk')


class TypeCorrectionTests(unittest.TestCase):
    def test_reproduction_outcome_after_type_correction(self):
        ds = [decision(field='type', corrected_value='reproduction'),
              decision(field='outcome', corrected_value={'outcome_computation': 'computational issues', 'outcome_robustness': 'robustness challenges'})]
        rs, _, _ = compare(decisions=ds)
        self.assertEqual(rs[0]['type_final_verdict'], 'error')
        self.assertEqual(rs[0]['outcome_final_verdict'], 'error')
        self.assertIn('outcome_computation', rs[0]['suggested_correction'])
