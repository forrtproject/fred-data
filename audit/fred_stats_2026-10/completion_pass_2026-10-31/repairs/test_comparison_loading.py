"""Exercise the checkpoint loader used by comparison, without running main."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[2] / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from compare import load_checkpoint
from retries import failure
from schema import validate


class ComparisonLoadingTests(unittest.TestCase):
    def test_canonical_primary_results_survive_stale_unavailable_snapshot(self):
        for side in ('original', 'replication'):
            for status in ('done', 'locator_insufficient'):
                with self.subTest(side=side, status=status):
                    with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
                        root = Path(directory)
                        (root / 'extractions').mkdir()
                        (root / 'before_locator_enrichment').mkdir()
                        before = failure(1, 'Older pre-enrichment snapshot')
                        before[side]['status'] = 'paper_unavailable'
                        current = copy.deepcopy(before)
                        current[side].update(status=status, target_match=status == 'done',
                                             target_description='Primary paper obtained')
                        if status == 'done':
                            current[side]['n'].update(
                                value='123', confident=True, quote='Participants: 123',
                                location='p. 2', source_path=str(root / 'primary.txt'))
                        validate(before)
                        validate(current)
                        canonical = root / 'extractions' / '1.json'
                        archive = root / 'before_locator_enrichment' / '1.json'
                        canonical.write_text(json.dumps(current))
                        archive.write_text(json.dumps(before))
                        canonical_bytes, archive_bytes = canonical.read_bytes(), archive.read_bytes()
                        loaded = load_checkpoint(root, 1)
                        self.assertEqual(loaded[side]['status'], status)
                        self.assertEqual(loaded, current)
                        self.assertEqual(canonical.read_bytes(), canonical_bytes)
                        self.assertEqual(archive.read_bytes(), archive_bytes)

    def test_missing_checkpoint_is_not_replaced_by_archive(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            (root / 'before_locator_enrichment').mkdir()
            (root / 'before_locator_enrichment' / '1.json').write_text(
                json.dumps(failure(1, 'Archived only')))
            self.assertIsNone(load_checkpoint(root, 1))

    def test_invalid_canonical_checkpoint_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            (root / 'extractions').mkdir()
            path = root / 'extractions' / '1.json'
            invalid = failure(1, 'Invalid failure side with a value')
            invalid['original']['n']['value'] = '123'
            path.write_text(json.dumps(invalid))
            with self.assertRaises(ValueError):
                load_checkpoint(root, 1)
            path.write_text(json.dumps(failure(2, 'Wrong audit ID')))
            with self.assertRaises(AssertionError):
                load_checkpoint(root, 1)


if __name__ == '__main__':
    unittest.main()
