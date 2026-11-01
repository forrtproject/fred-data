import subprocess
import unittest
from pathlib import Path
class ReviewReliabilityTests(unittest.TestCase):
    def test_old_approvals_cannot_bypass_current_holds(self):
        p=subprocess.run(['node',str(Path(__file__).with_suffix('.cjs'))],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
