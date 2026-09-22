#!/usr/bin/env python3
"""Compose a candidate public site; never deploy it or change canonical URLs.

Only explicit public files are read. Remote sources are pinned GitHub commits,
without credentials; Starter comes from the current build checkout. The lock
is for website composition, NOT downstream project adoption.
"""
from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
STARTER = "ChongLiuPhil/Inquiry-Publishing-Project-Starter"
REPOSITORIES = {
    "ahicp": "ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol",
    "ppf": "ChongLiuPhil/Personal-Publishing-Framework",
    "vault_interface": "ChongLiuPhil/Vault-interface",
    "starter": STARTER,
}
MOUNTS = {"ahicp": "/ahicp/", "ppf": "/ppf/", "vault_interface": "/vault-interface/", "starter": "/starter/"}
CURRENT = {k: "https://chongliuphil.github.io/" + v.split("/")[1] + "/" for k, v in REPOSITORIES.items()}
MACHINE_ENTRY = CURRENT["starter"] + "agent/"
# Deliberately narrow: additions require code + lock review, never a docs/** glob.
ALLOWED = {
    "ahicp": {"docs/index.html", "docs/HUMAN_GUIDE.md", "docs/HUMAN_GUIDE.zh-CN.md", "docs/llms.txt"},
    "ppf": {"docs/index.html", "docs/llms.txt"},
    "vault_interface": {"docs/index.html", "docs/llms.txt"},
    "starter": {"docs/index.html", "docs/llms.txt", "docs/agent/index.html", "docs/agent/entry.json", "docs/agent/bootstrap.txt", "docs/agent/bootstrap.zh-CN.txt", "docs/AGENT_RETRIEVAL_CONTRACT.md", "docs/AGENT_RETRIEVAL_CONTRACT.zh-CN.md", "docs/CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.md", "docs/CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.zh-CN.md"},
}
MAX_BYTES = 2_000_000
CSS = """.stack-nav,.stack-notice,.stack-source{font-family:system-ui,sans-serif;line-height:1.6;padding:12px 22px;margin:0;background:#f1f6f4;color:#17352d;border-bottom:1px solid #ccdcd4;overflow-wrap:anywhere}.stack-nav{display:flex;flex-wrap:wrap;align-items:center;gap:16px}.stack-nav a,.stack-source a,.stack-notice a{color:#17352d;font-weight:650}.stack-nav a:focus-visible{outline:3px solid #517b6d;outline-offset:4px}.stack-nav strong{margin-right:auto}.stack-notice{font-size:.9rem}.stack-source{margin-top:32px;font-size:.85rem}html[lang^=en] .stack-zh{display:none}html:not([lang^=en]) .stack-en{display:none}.stack-page{font-family:system-ui,sans-serif;max-width:850px;margin:auto;padding:40px 22px;line-height:1.8;color:#17352d}.stack-page h1{font-size:clamp(2rem,6vw,3.5rem);line-height:1.2}.stack-page pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f6f4;padding:20px;border-radius:12px}.stack-page a{color:#145b64}.stack-page li{margin:12px 0}@media(max-width:600px){.stack-nav{gap:10px}.stack-nav strong{width:100%}}"""


def validate_lock(lock: dict) -> None:
    if lock.get("schema") != "inquiry-publishing-stack/public-site-sources/v1" or lock.get("policy") != "explicit-public-file-allowlist":
        raise ValueError("Unsupported public-site lock")
    components = lock.get("components", {})
    if set(components) != set(REPOSITORIES):
        raise ValueError("Exactly four independent component sources are required")
    for key, component in components.items():
        if component.get("repository") != REPOSITORIES[key] or component.get("mount") != MOUNTS[key]:
            raise ValueError(f"Unexpected source or mount: {key}")
        revision = component.get("revision", "")
        if key == "starter":
            if revision != "build-checkout":
                raise ValueError("Starter must use the build checkout, not a self-referential commit pin")
        elif not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise ValueError(f"Unpinned upstream: {key}")
        files = component.get("files", [])
        if len(files) != len(set(files)) or set(files) != ALLOWED[key]:
            raise ValueError(f"Public file allowlist mismatch: {key}")


def destination(key: str, path: str) -> str:
    if key == "starter" and path.startswith("docs/agent/"):
        return "/" + path.removeprefix("docs/")
    if key == "starter" and path != "docs/index.html":
        return "/" + path.removeprefix("docs/")
    return MOUNTS[key] + path.removeprefix("docs/")


def rewrite_link(value: str, key: str, source: str, revision: str) -> str:
    if not value or value.startswith(("#", "mailto:", "tel:", "data:")):
        return value
    parts = urlsplit(value)
    if parts.scheme or parts.netloc:
        for target_key, current in CURRENT.items():
            # Only site URLs are rewritten. GitHub normative URLs remain upstream.
            if value.startswith(current):
                relative = value[len(current):]
                target = "docs/" + urlsplit(relative).path
                if not target.endswith(".html") and target.endswith("/"):
                    target += "index.html"
                if target == "docs/":
                    target = "docs/index.html"
                if target in ALLOWED[target_key]:
                    dest = destination(target_key, target)
                    if dest.endswith("index.html"):
                        dest = dest.removesuffix("index.html")
                    p = urlsplit(relative)
                    return urlunsplit(("", "", dest, p.query, p.fragment))
        return value
    resolved = urlsplit(urljoin("https://source.invalid/" + source, value))
    path = resolved.path.lstrip("/")
    if path in ALLOWED[key]:
        dest = destination(key, path)
        if dest.endswith("index.html"):
            dest = dest.removesuffix("index.html")
        return urlunsplit(("", "", dest, resolved.query, resolved.fragment))
    # Unpublished source files are not copied into the web output.
    return f"https://github.com/{REPOSITORIES[key]}/blob/{revision}/{path}" + ("#" + resolved.fragment if resolved.fragment else "")


class LinkRewriter(HTMLParser):
    """Preserve script/style/text verbatim; rewrite actual HTML attributes only."""
    def __init__(self, key: str, source: str, revision: str):
        super().__init__(convert_charrefs=False)
        self.key, self.source, self.revision = key, source, revision
        self.output: list[str] = []

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text()
        def sub(match):
            name, quote, value = match.group(1), match.group(2), match.group(3)
            rewritten = rewrite_link(html.unescape(value), self.key, self.source, self.revision)
            return name + "=" + quote + html.escape(rewritten, quote=True) + quote
        raw = re.sub(r"\b(href)\s*=\s*([\"'])(.*?)\2", sub, raw, flags=re.I | re.S)
        self.output.append(raw)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag): self.output.append(f"</{tag}>")
    def handle_data(self, data): self.output.append(data)
    def handle_entityref(self, name): self.output.append(f"&{name};")
    def handle_charref(self, name): self.output.append(f"&#{name};")
    def handle_comment(self, data): self.output.append(f"<!--{data}-->")
    def handle_decl(self, decl): self.output.append(f"<!{decl}>")
    def handle_pi(self, data): self.output.append(f"<?{data}>")


def chrome(text: str, key: str, revision: str) -> str:
    nav = '<nav class="stack-nav" aria-label="Inquiry Publishing Stack"><strong><a href="/">Inquiry Publishing Stack</a></strong><a href="/start/"><span class="stack-zh">开始</span><span class="stack-en">Start</span></a>'
    for label, path in (("AHICP", "/ahicp/"), ("PPF", "/ppf/"), ("Vault Interface", "/vault-interface/"), ("Starter", "/starter/"), ("AI Agent", "/agent/")):
        nav += f'<a href="{path}">{label}</a>'
    nav += '</nav>'
    notice = '<aside class="stack-notice"><span class="stack-zh">单站迁移候选版本，尚未正式切换。<a href="' + CURRENT["ahicp"] + '">当前正式人类入口</a>；<a href="' + MACHINE_ENTRY + '">当前正式机器入口</a>。</span><span class="stack-en">Unified-site candidate, not a public cutover. <a href="' + CURRENT["ahicp"] + '">Current human entry</a>; <a href="' + MACHINE_ENTRY + '">current machine entry</a>.</span></aside>'
    footer = '<footer class="stack-source">Source: <a href="https://github.com/' + REPOSITORIES[key] + '/tree/' + revision + '">' + key + ' @ ' + revision[:12] + '</a> · <a href="/build-info.json">Build provenance</a></footer>'
    if '</head>' not in text or '<body>' not in text or '</body>' not in text:
        raise ValueError(f"Expected a complete static HTML document: {key}")
    text = text.replace('</head>', '<meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="/assets/stack.css"></head>', 1)
    text = text.replace('<body>', '<body>' + nav + notice, 1)
    return text.replace('</body>', footer + '</body>', 1)


def start_page(english: bool) -> str:
    lang = "en" if english else "zh-CN"
    title = "Start with a question, not a toolchain" if english else "从你的问题开始，不必先学会工具"
    intro = "You choose the purpose, boundaries, and important decisions. AI helps recover the current project, organize evidence, and prepare the next steps." if english else "你决定目标、边界和重要判断。AI 帮你恢复项目状态、整理证据，并准备可以继续的下一步。"
    steps = (["Describe the question or work you want to pursue.", "Choose a new project or identify an existing repository. Private access requires your explicit authorization.", "Give the current machine-entry URL to your agent. It must read the latest contracts before acting."] if english else ["说明你想研究的问题或准备完成的作品。", "说明是新项目，还是已有项目；访问私人仓库需要你的明确授权。", "把当前正式机器入口交给 AI，让它先读取最新契约，再开始配置或升级。"])
    default = "Default: full AHICP + full PPF + Vault Interface. Original sources stay private; unpublished Web stays restricted and authenticated. Publication needs separate human approval." if english else "默认完整 AHICP + 完整 PPF + Vault Interface。原创源文件默认 private；未发布 Web 默认 restricted + authenticated。公开发布仍需你单独批准。"
    prompt = ("Read " + MACHINE_ENTRY + " and reconstruct the current Inquiry Publishing Stack. Help me start or resume my project; preserve my work, private state, and approval boundaries." if english else "请读取 " + MACHINE_ENTRY + "，恢复 Inquiry Publishing Stack 的当前状态，帮助我开始或继续项目；保留项目已有内容、私人状态与人类批准边界。")
    switch = '<a href="/start/">中文</a>' if english else '<a href="/start/index.en.html">English</a>'
    return '<!doctype html><html lang="' + lang + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + title + '</title></head><body><main class="stack-page">' + switch + '<h1>' + title + '</h1><p>' + intro + '</p><ol>' + ''.join('<li>' + x + '</li>' for x in steps) + '</ol><pre>' + html.escape(prompt) + '</pre><p>' + default + '</p><p><a href="/ahicp/#start-now-' + ('en' if english else 'zh') + '">' + ('Read the AHICP start guide' if english else '阅读 AHICP 使用指南') + '</a> · <a href="/agent/">AI Agent</a></p></main></body></html>'


def remote_source(repository: str, revision: str, path: str) -> bytes:
    url = f"https://raw.githubusercontent.com/{repository}/{revision}/{path}"
    request = Request(url, headers={"User-Agent": "Inquiry-Publishing-Stack-public-site-builder"})
    with urlopen(request, timeout=45) as response:
        # Never follow a source request to an unexpected host or login surface.
        if urlsplit(response.url).hostname != "raw.githubusercontent.com":
            raise ValueError("Unexpected public-source redirect")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Public source exceeds size limit")
    data.decode("utf-8")
    return data


def checkout_revision(root: Path) -> tuple[str, bool]:
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Cannot identify Starter build revision")
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=root, text=True).strip())
    return revision, dirty


def compose(root: Path, output: Path, lock: dict, revision: str, dirty: bool, loader=remote_source) -> dict:
    validate_lock(lock)
    output.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    source_info: dict = {}
    for key, component in lock["components"].items():
        ref = revision if key == "starter" else component["revision"]
        source_info[key] = {"repository": component["repository"], "revision": ref, "files": {}}
        for path in component["files"]:
            data = (root / path).read_bytes() if key == "starter" else loader(component["repository"], ref, path)
            if len(data) > MAX_BYTES:
                raise ValueError("Oversized public source")
            text = data.decode("utf-8")
            source_info[key]["files"][path] = hashlib.sha256(data).hexdigest()
            if path.endswith(".html"):
                parser = LinkRewriter(key, path, ref)
                parser.feed(text)
                text = chrome(''.join(parser.output), key, ref)
            elif path.endswith(".md"):
                text = re.sub(r"\]\(([^\s)]+)\)", lambda m: '](' + rewrite_link(m.group(1), key, path, ref) + ')', text)
            files[destination(key, path)] = text
    # Root is derived from AHICP's human introduction, not a fourth specification.
    # Keep all substantive content and the existing Chinese/no-JavaScript fallback.
    home = files["/ahicp/index.html"]
    home = home.replace('<div class="brand">AHICP</div>', '<div class="brand">Inquiry Publishing Stack</div>', 1)
    home = re.sub(r"<title>.*?</title>", "<title>Inquiry Publishing Stack · AHICP</title>", home, count=1)
    files["/index.html"] = home
    # The upstream human guide loader uses relative filenames on both routes.
    for name in ("HUMAN_GUIDE.md", "HUMAN_GUIDE.zh-CN.md"):
        files["/" + name] = files["/ahicp/" + name]
    files["/start/index.html"] = chrome(start_page(False), "starter", revision)
    files["/start/index.en.html"] = chrome(start_page(True), "starter", revision)
    descriptor = json.loads(files["/agent/entry.json"])
    if descriptor.get("public_landing") != MACHINE_ENTRY or descriptor.get("human_entry") != CURRENT["ahicp"]:
        raise ValueError("Current public entries changed: implement separately authorized cutover first")
    descriptor["delivery_candidate"] = {"state": "not-cutover", "topology": "single-site-multi-repository", "human_path": "/", "machine_path": "/agent/", "custom_domain": None, "build_provenance": "/build-info.json"}
    files["/agent/entry.json"] = json.dumps(descriptor, ensure_ascii=False, indent=2) + "\n"
    files["/llms.txt"] += "\nUnified-site candidate routes (not canonical URLs):\n/ = AHICP-led human entry\n/agent/ = Starter machine entry\n/agent/entry.json = descriptor\n/build-info.json = source revisions and content hashes\nCurrent public entrypoints above remain unchanged until explicit verified cutover.\n"
    files["/assets/stack.css"] = CSS + "\n"
    files["/404.html"] = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Not found</title></head><body><h1>Not found</h1><a href="/">Inquiry Publishing Stack</a></body></html>'
    files["/robots.txt"] = "User-agent: *\nDisallow: /\n"
    files["/_headers"] = "/*\n  X-Robots-Tag: noindex, nofollow\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n"
    provenance = {"schema": "inquiry-publishing-stack/public-site-build/v1", "state": "candidate-not-cutover", "starter_revision": revision, "working_tree_dirty": dirty, "source_lock_sha256": hashlib.sha256((root / "site/sources.lock.json").read_bytes()).hexdigest(), "components": source_info, "outputs": {p: hashlib.sha256(t.encode()).hexdigest() for p, t in sorted(files.items())}}
    files["/build-info.json"] = json.dumps(provenance, ensure_ascii=False, indent=2) + "\n"
    for path, text in files.items():
        target = output / path.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return provenance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--holding", action="store_true", help="Deploy only an empty holding page while Access is being configured")
    args = parser.parse_args()
    output = ROOT / "_site"
    if output.is_symlink():
        raise ValueError("Refusing a symlink output directory")
    with tempfile.TemporaryDirectory(prefix="public-site-", dir=ROOT) as temporary:
        stage = Path(temporary)
        if args.holding:
            (stage / "index.html").write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><title>Setup pending</title></head><body><h1>Setup pending</h1></body></html>\n')
            (stage / "_headers").write_text('/*\n  X-Robots-Tag: noindex, nofollow\n')
            (stage / "robots.txt").write_text('User-agent: *\nDisallow: /\n')
        else:
            lock = json.loads((ROOT / "site/sources.lock.json").read_text())
            revision, dirty = checkout_revision(ROOT)
            compose(ROOT, stage, lock, revision, dirty)
            # Validation is part of the Cloudflare build, not only the GitHub CI.
            from validate_public_site import validate
            validate(stage)
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(stage, output)
    print("Holding page ready" if args.holding else "Unified-site candidate validated; no deployment or public cutover performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
