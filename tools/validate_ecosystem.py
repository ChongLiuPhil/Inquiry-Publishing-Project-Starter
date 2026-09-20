from pathlib import Path
import json
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
CORE_REPOSITORIES = [
    "https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol",
    "https://github.com/ChongLiuPhil/Personal-Publishing-Framework",
    "https://github.com/ChongLiuPhil/Vault-interface",
    "https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter",
]
HUMAN_ENTRY = "https://chongliuphil.github.io/AI-Assisted-Human-Inquiry-and-Creation-Protocol/"
MACHINE_ENTRY = "https://chongliuphil.github.io/Inquiry-Publishing-Project-Starter/agent/"


def main() -> int:
    manifest = yaml.safe_load((ROOT / "ecosystem.yaml").read_text())
    ecosystem = manifest.get("ecosystem") if isinstance(manifest, dict) else None
    if not isinstance(ecosystem, dict) or "canonical_entrypoint" not in ecosystem:
        raise SystemExit("ecosystem.yaml is missing canonical_entrypoint")

    human = ecosystem.get("human_entrypoint")
    machine = ecosystem.get("machine_entrypoint")
    if not isinstance(human, dict) or human.get("current_public_landing") != HUMAN_ENTRY:
        raise SystemExit("Starter ecosystem is missing the AHICP human entry")
    if not human.get("provider_may_change"):
        raise SystemExit("human entry must remain delivery-provider independent")
    if not isinstance(machine, dict) or machine.get("public_landing") != MACHINE_ENTRY:
        raise SystemExit("Starter ecosystem is missing the stable /agent/ machine entry")

    manifest_text = (ROOT / "ecosystem.yaml").read_text()
    for repository in CORE_REPOSITORIES:
        if repository not in manifest_text:
            raise SystemExit(f"ecosystem.yaml is missing {repository}")

    for relative in ("README.md", "README.zh-CN.md"):
        text = (ROOT / relative).read_text()
        if "ecosystem.yaml" not in text and "docs/ECOSYSTEM" not in text:
            raise SystemExit(f"{relative} does not point to the ecosystem entrypoint")

    required_agent_files = (
        "docs/agent/index.html",
        "docs/agent/bootstrap.txt",
        "docs/agent/bootstrap.zh-CN.txt",
        "docs/agent/entry.json",
    )
    for relative in required_agent_files:
        if not (ROOT / relative).exists():
            raise SystemExit(f"missing public machine-entry artifact: {relative}")

    descriptor = json.loads((ROOT / "docs/agent/entry.json").read_text(encoding="utf-8"))
    if descriptor.get("public_landing") != MACHINE_ENTRY:
        raise SystemExit("agent entry descriptor has the wrong public landing")
    if descriptor.get("human_entry") != HUMAN_ENTRY:
        raise SystemExit("agent entry descriptor has the wrong human entry")

    agent_page = (ROOT / "docs/agent/index.html").read_text(encoding="utf-8")
    for marker in ("Agent Retrieval Contract", "ecosystem.yaml", "bootstrap.txt", HUMAN_ENTRY):
        if marker not in agent_page:
            raise SystemExit(f"machine-entry page is missing {marker}")

    root_page = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    if MACHINE_ENTRY not in root_page:
        raise SystemExit("Starter homepage does not expose the public machine entry")

    print("ecosystem + machine-entry validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
