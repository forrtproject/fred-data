"""Exercise the pure shared log reducer through the actual JavaScript module."""
import subprocess
import unittest
from pathlib import Path

class SharedReviewProtocolTests(unittest.TestCase):
    def test_concurrent_reviewers_and_partial_network_writes(self):
        result=subprocess.run(['node',str(Path(__file__).with_name('test_review_shared_state.cjs'))],capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=='__main__':unittest.main()
