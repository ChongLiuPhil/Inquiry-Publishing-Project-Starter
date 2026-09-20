import subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class StackContractTests(unittest.TestCase):
    def run_check(self, fixture):
        return subprocess.run([sys.executable,str(ROOT/"tools/stack.py"),"check","--root",str(ROOT/"tests/fixtures"/fixture)],
                              text=True,capture_output=True)
    def test_research_book_allows_deferred_ppf(self):
        r=self.run_check("research-book-deferred"); self.assertEqual(r.returncode,0,r.stderr+r.stdout)
    def test_full_profile_supports_dual_ppf_revisions_and_legacy_mapping(self):
        r=self.run_check("full-legacy-dual-revision"); self.assertEqual(r.returncode,0,r.stderr+r.stdout)
    def test_generated_lock_rejects_template_placeholder(self):
        r=self.run_check("invalid-generated-placeholder"); self.assertNotEqual(r.returncode,0)
        self.assertIn("real Starter source commit",r.stderr)
if __name__=="__main__": unittest.main()
