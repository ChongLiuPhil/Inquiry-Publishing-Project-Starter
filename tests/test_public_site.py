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
                    return json.dumps({
                        "public_landing": MACHINE_ENTRY,
                        "human_entry": PUBLIC_URL,
                        "public_delivery": {"current_provider": "cloudflare-workers"},
                        "authorization": {"deployment_token_plaintext_in_model_context": False},
                        "project_provisioning": {
                            "preferred_profile": "workers-builds-native",
                            "default_setup_mode": "human-assisted-once-per-project",
                            "default_access_mode": "worker-scoped-access",
                            "default_ci_cost_profile": "private-project-quota-saver",
                            "secret_broker_required_for_default": False,
                            "status": "guided-per-project-default",
                            "per_project_setup_contract": "https://github.com/ChongLiuPhil/Personal-Publishing-Framework/blob/main/docs/PER_PROJECT_GITHUB_CLOUDFLARE_SETUP.md",
                            "ci_cost_policy": "https://github.com/ChongLiuPhil/Personal-Publishing-Framework/blob/main/docs/CI_COST_POLICY.md",
                            "private_project_github_actions": {
                                "content_only_changes": "none",
                                "configuration_pull_request": "light-contract-check",
                                "main_push": "none",
                                "heavy_validation": "manual",
                            },
                        },
                    }).encode()
                return b'Public fixture text\n'
            for path in ALLOWED["starter"]:
                file = root / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(fixture(REPOSITORIES["starter"], "a" * 40, path))
            out = Path(temp) / "out"
            info = compose(root, out, self.lock, "a" * 40, False, fixture)
            validate(out)
            self.assertEqual(info["components"]["starter"]["revision"], "a" * 40)
            descriptor = json.loads((out / "agent/entry.json").read_text())
            self.assertEqual(descriptor["public_landing"], MACHINE_ENTRY)
            self.assertEqual(descriptor["project_provisioning"]["preferred_profile"], "workers-builds-native")
            self.assertEqual(descriptor["project_provisioning"]["default_ci_cost_profile"], "private-project-quota-saver")
            self.assertEqual(descriptor["project_provisioning"]["private_project_github_actions"]["content_only_changes"], "none")
            self.assertTrue((out / "PROJECT_PROVISIONING_CONTRACT.md").is_file())
            self.assertTrue((out / "PROJECT_PROVISIONING_ACCEPTANCE.md").is_file())
            start_zh = (out / "start/index.html").read_text(encoding="utf-8")
            start_en = (out / "start/index.en.html").read_text(encoding="utf-8")
            self.assertIn("workers-builds-native", start_zh)
            self.assertIn("private-project-quota-saver", start_zh)
            self.assertIn("第二次 push", start_zh)
            self.assertIn("workers-builds-native", start_en)
            self.assertIn("private-project-quota-saver", start_en)
            self.assertIn("second push", start_en)
            self.assertNotIn("平台 bootstrap 已验证后", start_zh)
            self.assertNotIn("agent-provisioned-external-ci", start_en)
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
