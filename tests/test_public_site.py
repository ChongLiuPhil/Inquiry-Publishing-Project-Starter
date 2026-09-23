"""Offline unit/regression tests. Live-source integration runs separately in CI."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_public_site import ALLOWED, CURRENT, MACHINE_ENTRY, PUBLIC_URL, REPOSITORIES, LinkRewriter, compose, rewrite_link, validate_lock
from validate_public_site import validate


class PublicSiteTests(unittest.TestCase):
    def setUp(self):
        self.lock = json.loads((ROOT / "site/sources.lock.json").read_text())

    def test_lock_accepts_exact_public_inputs(self):
        validate_lock(self.lock)

    def test_floating_ref_rejected(self):
        self.lock["components"]["ahicp"]["revision"] = "main"
        with self.assertRaises(ValueError): validate_lock(self.lock)

    def test_private_or_extra_file_rejected(self):
        self.lock["components"]["ahicp"]["files"].append("docs/working-memory/current-focus.zh-CN.md")
        with self.assertRaises(ValueError): validate_lock(self.lock)

    def test_other_repository_rejected(self):
        self.lock["components"]["ppf"]["repository"] = "someone/private-project"
        with self.assertRaises(ValueError): validate_lock(self.lock)

    def test_path_traversal_rejected(self):
        self.lock["components"]["starter"]["files"].append("../private.txt")
        with self.assertRaises(ValueError): validate_lock(self.lock)

    def test_site_links_move_but_bootstrap_text_does_not(self):
        source = '<html><body><a href="' + MACHINE_ENTRY + '">Agent</a><textarea>' + MACHINE_ENTRY + '</textarea><script>const url="' + MACHINE_ENTRY + '";</script></body></html>'
        parser = LinkRewriter("ahicp", "docs/index.html", "a" * 40)
        parser.feed(source)
        text = ''.join(parser.output)
        self.assertIn('href="/agent/"', text)
        self.assertIn('<textarea>' + MACHINE_ENTRY, text)
        self.assertIn('const url="' + MACHINE_ENTRY, text)

    def test_relative_nonpublished_document_stays_upstream(self):
        actual = rewrite_link("../README.md#start", "ppf", "docs/index.html", "a" * 40)
        self.assertEqual(actual, "https://github.com/" + REPOSITORIES["ppf"] + "/blob/" + "a" * 40 + "/README.md#start")

    def test_agent_relative_resource_is_local(self):
        self.assertEqual(rewrite_link("entry.json", "starter", "docs/agent/index.html", "a" * 40), "/agent/entry.json")

    def test_full_fixture_build_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "source"
            root.mkdir()
            (root / "site").mkdir()
            (root / "site/sources.lock.json").write_text(json.dumps(self.lock))
            (root / "templates").mkdir()
            (root / "templates/cloudflare-public-delivery.yaml").write_bytes((ROOT / "templates/cloudflare-public-delivery.yaml").read_bytes())
            def fixture(repository, revision, path):
                if path.endswith(".html"):
                    return b'<!doctype html><html lang="zh-CN"><head><title>Fixture</title></head><body><main id="zh" class="lang active"><h1>Fixture content</h1><a href="#x" id="x">Link</a></main><script>const ok = true;</script></body></html>'
                if path.endswith("entry.json"):
                    return json.dumps({"public_landing": MACHINE_ENTRY, "human_entry": PUBLIC_URL, "public_delivery": {"current_provider": "cloudflare-workers"}}).encode()
                return b'Public fixture text\n'
            for path in ALLOWED["starter"]:
                file = root / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(fixture(REPOSITORIES["starter"], "a" * 40, path))
            out = Path(temp) / "out"
            info = compose(root, out, self.lock, "a" * 40, False, fixture)
            validate(out)
            self.assertEqual(info["components"]["starter"]["revision"], "a" * 40)
            self.assertEqual(json.loads((out / "agent/entry.json").read_text())["public_landing"], MACHINE_ENTRY)
            self.assertFalse((out / "docs/working-memory").exists())
            first = (out / "build-info.json").read_bytes()
            compose(root, out, self.lock, "a" * 40, False, fixture)
            self.assertEqual(first, (out / "build-info.json").read_bytes())
            plan = root / "templates/cloudflare-public-delivery.yaml"
            approved = plan.read_text()
            plan.write_text(approved.replace("public_cutover_authorized: true", "public_cutover_authorized: false"))
            with self.assertRaisesRegex(ValueError, "not authorized"):
                compose(root, out, self.lock, "a" * 40, False, fixture)
            plan.write_text(approved)
            (out / "index.html").write_text("tampered")
            with self.assertRaises(ValueError): validate(out)


if __name__ == "__main__":
    unittest.main()
