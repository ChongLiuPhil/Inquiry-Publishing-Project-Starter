import subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class StackContractTests(unittest.TestCase):
    def run_check(self, fixture):
        return subprocess.run([sys.executable,str(ROOT/"tools/stack.py"),"check","--root",str(ROOT/"tests/fixtures"/fixture)],
                              text=True,capture_output=True)

    def assert_fixture_valid(self, name):
        r=self.run_check(name)
        self.assertEqual(r.returncode,0,r.stderr+r.stdout)

    def test_research_only_profile(self):
        self.assert_fixture_valid("research-only")

    def test_publishing_only_profile(self):
        self.assert_fixture_valid("publishing-only")

    def test_research_book_allows_deferred_ppf(self):
        self.assert_fixture_valid("research-book-deferred")

    def test_full_profile_supports_dual_ppf_revisions_and_legacy_mapping(self):
        self.assert_fixture_valid("full-legacy-dual-revision")

    def test_generated_lock_rejects_template_placeholder(self):
        r=self.run_check("invalid-generated-placeholder")
        self.assertNotEqual(r.returncode,0)

if __name__=="__main__":
    unittest.main()
