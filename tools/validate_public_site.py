#!/usr/bin/env python3
"""Validate the assembled public site, including provenance, links and cutover gates."""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ("index.html", "start/index.html", "start/index.en.html", "ahicp/index.html", "ppf/index.html", "vault-interface/index.html", "starter/index.html", "agent/index.html")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.h1 = False
        self.has_title = False
        self.ids = set()
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.h1 |= tag == "h1"
        self.has_title |= tag == "title"
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.links.append(attrs[attr])


def validate(output: Path) -> None:
    info = json.loads((output / "build-info.json").read_text())
    public_url = "https://inquirystack.philohub.workers.dev/"
    if info.get("state") != "canonical-workers-dev" or info.get("public_url") != public_url:
        raise ValueError("Public build identity does not match the approved Worker")
    if set(info.get("components", {})) != {"ahicp", "ppf", "vault_interface", "starter"}:
        raise ValueError("Missing independent component provenance")
    for component in info["components"].values():
        if not re.fullmatch(r"[0-9a-f]{40}", component.get("revision", "")):
            raise ValueError("Unresolved source revision")
    actual_files = {"/" + p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
    if actual_files != set(info["outputs"]) | {"/build-info.json"}:
        raise ValueError("Unexpected output files or missing provenance")
    for path, checksum in info["outputs"].items():
        file = output / path.lstrip("/")
        if file.is_symlink():
            raise ValueError(f"Output integrity failure: {path}")
        contents = file.read_bytes()
        if hashlib.sha256(contents).hexdigest() != checksum:
            raise ValueError(f"Output integrity failure: {path}")
        if b"chongliuphil.github.io" in contents.lower():
            raise ValueError(f"Retired GitHub Pages URL leaked into public output: {path}")
    descriptor = json.loads((output / "agent/entry.json").read_text())
    if descriptor.get("public_landing") != public_url + "agent/" or descriptor.get("human_entry") != public_url or descriptor.get("public_delivery", {}).get("current_provider") != "cloudflare-workers":
        raise ValueError("Machine entry does not identify the approved Worker")
    provisioning = descriptor.get("project_provisioning", {})
    if (
        provisioning.get("preferred_profile") != "workers-builds-native"
        or provisioning.get("default_setup_mode") != "human-assisted-once-per-project"
        or provisioning.get("default_access_mode") != "worker-scoped-access"
        or provisioning.get("default_ci_cost_profile") != "private-project-quota-saver"
        or provisioning.get("secret_broker_required_for_default") is not False
    ):
        raise ValueError("Machine entry does not expose the guided per-project provisioning contract")
    if provisioning.get("status") != "guided-per-project-default":
        raise ValueError("Machine entry lost the guided per-project provisioning status")
    expected_actions = {
        "content_only_changes": "none",
        "configuration_pull_request": {
            "target_branch": "main",
            "class": "light-contract-check",
            "timeout_minutes": 5,
        },
        "main_push": "none",
        "heavy_validation": "manual",
        "artifact_policy": {
            "automatic_success_upload": False,
            "manual_publication_retention_days": 1,
            "diagnostic_retention_days": 1,
        },
        "retry": "failed-job-or-workflow-only",
    }
    if provisioning.get("private_project_github_actions") != expected_actions:
        raise ValueError("Machine entry lost the private-project GitHub Actions quota policy")
    expected_tiers = {
        "ordinary_private": {
            "mode": "quota-saver-native",
            "infrastructure_profile": "workers-builds-native",
            "ci_cost_profile": "private-project-quota-saver",
        },
        "hardened_external_ci": {
            "mode": "hardened-external-ci",
            "infrastructure_profile": "agent-provisioned-external-ci",
            "ci_cost_profile": "external-ci-required",
        },
        "public_framework": {
            "mode": "full-ci",
            "ci_cost_profile": "full-validation",
        },
    }
    if provisioning.get("ci_profile_tiers") != expected_tiers:
        raise ValueError("Machine entry lost the CI profile tier contract")
    if not str(provisioning.get("ci_cost_policy", "")).endswith("/docs/CI_COST_POLICY.md"):
        raise ValueError("Machine entry does not expose the PPF CI cost policy")
    if not str(provisioning.get("per_project_setup_contract", "")).endswith("/docs/PER_PROJECT_GITHUB_CLOUDFLARE_SETUP.md"):
        raise ValueError("Machine entry does not expose the PPF per-project setup contract")
    if descriptor.get("authorization", {}).get("deployment_token_plaintext_in_model_context") is not False:
        raise ValueError("Machine entry must keep deployment-token plaintext out of model context")
    for path in (
        "agent/bootstrap.txt",
        "agent/bootstrap.zh-CN.txt",
        "llms.txt",
        "PROJECT_PROVISIONING_CONTRACT.md",
        "PROJECT_PROVISIONING_CONTRACT.zh-CN.md",
        "PROJECT_PROVISIONING_ACCEPTANCE.md",
        "PROJECT_PROVISIONING_ACCEPTANCE.zh-CN.md",
        "HUMAN_GUIDE.md",
        "HUMAN_GUIDE.zh-CN.md",
        "ahicp/HUMAN_GUIDE.md",
        "ahicp/HUMAN_GUIDE.zh-CN.md",
    ):
        if not (output / path).is_file() or not (output / path).stat().st_size:
            raise ValueError(f"Missing machine/guide resource: {path}")
    if "noindex" in (output / "_headers").read_text() or "Disallow: /" in (output / "robots.txt").read_text():
        raise ValueError("Canonical public site must not carry candidate indexing restrictions")
    for route in sorted(set(ROUTES) | {p.relative_to(output).as_posix() for p in output.rglob("*.html")}):
        page_path = output / route
        text = page_path.read_text(encoding="utf-8")
        page = Page()
        page.feed(text)
        if route in ROUTES and (not page.h1 or not page.has_title or 'class="stack-nav"' not in text):
            raise ValueError(f"Missing visible content/navigation: {route}")
        if route != "404.html":
            path = route.removesuffix("index.html") if route.endswith("index.html") else route
            expected = public_url + path
            if page.canonicals != [expected] or 'noindex' in text.lower():
                raise ValueError(f"Canonical URL or indexing gate failed: {route}")
        if route in ("index.html", "ahicp/index.html", "ppf/index.html", "vault-interface/index.html", "starter/index.html"):
            if not re.search(r'id="zh"\s+class="[^\"]*\bactive\b', text):
                raise ValueError(f"Chinese no-JavaScript fallback missing: {route}")
        for link in page.links:
            resolved = urlsplit(urljoin("https://candidate.invalid/" + route, link))
            if resolved.netloc != "candidate.invalid" or resolved.scheme not in ("http", "https"):
                continue
            path = unquote(resolved.path).lstrip("/")
            target = (output / path).resolve()
            if not target.is_relative_to(output.resolve()):
                raise ValueError(f"Path escapes output: {link}")
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                raise ValueError(f"Broken local URL in {route}: {link}")
        scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", text, flags=re.S | re.I)
        for script in scripts:
            with tempfile.TemporaryDirectory() as temp:
                script_path = Path(temp) / "check.js"
                script_path.write_text(script)
                result = subprocess.run(["node", "--check", str(script_path)], text=True, capture_output=True)
                if result.returncode:
                    raise ValueError(f"JavaScript failure in {route}: {result.stderr}")
    print(f"PASS: {len(ROUTES)} HTML routes, local links, source revisions, output hashes, JavaScript, canonical identity gates")


if __name__ == "__main__":
    validate(ROOT / "_site")
