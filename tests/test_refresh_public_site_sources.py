import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from refresh_public_site_sources import refresh


class RefreshPublicSiteSourcesTests(unittest.TestCase):
    def setUp(self):
        self.lock = json.loads((Path(__file__).resolve().parents[1] / "site/sources.lock.json").read_text())

    def test_updates_pin_only_when_allowlisted_file_changes(self):
        component = self.lock["components"]["ppf"]
        old_revision = component["revision"]
        latest = "a" * 40
        old_content = {path: b"old" for path in component["files"]}
        new_content = dict(old_content)
        new_content[component["files"][1]] = b"new public content"
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "sources.lock.json"
            lock_path.write_text(json.dumps(self.lock))
            changed = refresh(
                lock_path,
                apply=True,
                resolve=lambda repository: latest if repository == component["repository"] else self.lock["components"]["ahicp"]["revision"] if repository == self.lock["components"]["ahicp"]["repository"] else self.lock["components"]["vault_interface"]["revision"],
                read_file=lambda repository, revision, path: (new_content if revision == latest else old_content)[path],
            )
            updated = json.loads(lock_path.read_text())
        self.assertEqual(changed, ["ppf"])
        self.assertEqual(updated["components"]["ppf"]["revision"], latest)
        self.assertEqual(updated["components"]["ahicp"]["revision"], self.lock["components"]["ahicp"]["revision"])
        self.assertEqual(updated["components"]["vault_interface"]["revision"], self.lock["components"]["vault_interface"]["revision"])

    def test_ignores_new_commit_when_allowlisted_files_are_identical(self):
        latest = "b" * 40
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "sources.lock.json"
            original = json.dumps(self.lock)
            lock_path.write_text(original)
            changed = refresh(
                lock_path,
                apply=True,
                resolve=lambda repository: latest if repository == self.lock["components"]["ppf"]["repository"] else self.lock["components"]["ahicp"]["revision"] if repository == self.lock["components"]["ahicp"]["repository"] else self.lock["components"]["vault_interface"]["revision"],
                read_file=lambda repository, revision, path: b"same public bytes",
            )
            after = lock_path.read_text()
        self.assertEqual(changed, [])
        self.assertEqual(after, original)

    def test_fetch_failure_does_not_partially_write_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "sources.lock.json"
            original = json.dumps(self.lock)
            lock_path.write_text(original)
            def fail(repository, revision, path):
                raise RuntimeError("upstream unavailable")
            with self.assertRaises(RuntimeError):
                refresh(lock_path, apply=True, resolve=lambda _: "a"*40, read_file=fail)
            self.assertEqual(lock_path.read_text(), original)


if __name__ == "__main__":
    unittest.main()
