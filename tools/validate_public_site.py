#!/usr/bin/env python3
"""Validate the assembled candidate, including provenance, links, JS and gates."""
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

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.h1 |= tag == "h1"
        self.has_title |= tag == "title"
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.links.append(attrs[attr])


def validate(output: Path) -> None:
    info = json.loads((output / "build-info.json").read_text())
    if info.get("state") != "candidate-not-cutover":
        raise ValueError("This builder is not authorized for public cutover")
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
        if file.is_symlink() or hashlib.sha256(file.read_bytes()).hexdigest() != checksum:
            raise ValueError(f"Output integrity failure: {path}")
    descriptor = json.loads((output / "agent/entry.json").read_text())
    current = "https://chongliuphil.github.io/Inquiry-Publishing-Project-Starter/agent/"
    if descriptor.get("public_landing") != current or descriptor.get("public_delivery", {}).get("current_provider") != "github-pages":
        raise ValueError("Candidate must not replace current public identity")
    if descriptor.get("delivery_candidate", {}).get("custom_domain") is not None:
        raise ValueError("No custom domain is authorized")
    for path in ("agent/bootstrap.txt", "agent/bootstrap.zh-CN.txt", "llms.txt", "HUMAN_GUIDE.md", "HUMAN_GUIDE.zh-CN.md", "ahicp/HUMAN_GUIDE.md", "ahicp/HUMAN_GUIDE.zh-CN.md"):
        if not (output / path).is_file() or not (output / path).stat().st_size:
            raise ValueError(f"Missing machine/guide resource: {path}")
    if "noindex" not in (output / "_headers").read_text() or "Disallow: /" not in (output / "robots.txt").read_text():
        raise ValueError("Candidate must discourage indexing; this is not authentication")
    for route in ROUTES:
        page_path = output / route
        text = page_path.read_text(encoding="utf-8")
        page = Page()
        page.feed(text)
        if not page.h1 or not page.has_title or 'class="stack-nav"' not in text:
            raise ValueError(f"Missing visible content/navigation: {route}")
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
    print(f"PASS: {len(ROUTES)} HTML routes, local links, source revisions, output hashes, JavaScript, candidate identity gates")


if __name__ == "__main__":
    validate(ROOT / "_site")
