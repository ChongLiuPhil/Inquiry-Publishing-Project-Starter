from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile

import yaml


ROOT = Path(__file__).resolve().parents[1]
CORE_REPOSITORIES = [
    "https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol",
    "https://github.com/ChongLiuPhil/Personal-Publishing-Framework",
    "https://github.com/ChongLiuPhil/Vault-interface",
    "https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter",
]
HUMAN_ENTRY = "https://inquirystack.philohub.workers.dev/"
MACHINE_ENTRY = HUMAN_ENTRY + "agent/"


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

    migration_plan_path = ROOT / "templates/cloudflare-public-delivery.yaml"
    migration_guide_path = ROOT / "docs/CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.md"
    migration_guide_zh_path = ROOT / "docs/CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.zh-CN.md"
    for required_path in (migration_plan_path, migration_guide_path, migration_guide_zh_path):
        if not required_path.exists():
            raise SystemExit(f"missing Cloudflare public-delivery migration artifact: {required_path.relative_to(ROOT)}")

    migration_plan = yaml.safe_load(migration_plan_path.read_text(encoding="utf-8"))
    if migration_plan.get("preferred_public_delivery_provider") != "cloudflare-workers":
        raise SystemExit("Cloudflare Workers must be the preferred public delivery provider")
    if migration_plan.get("current_public_delivery_provider") != "cloudflare-workers":
        raise SystemExit("approved canonical Worker must be current")
    if migration_plan.get("cutover_rule") != "switch-public-entrypoints-only-after-verified-cloudflare-deployment":
        raise SystemExit("public URL cutover must require verified Cloudflare deployment")
    if migration_plan.get("build_defaults", {}).get("output_dir") != "_site":
        raise SystemExit("unified Cloudflare Workers output directory must be _site")
    if migration_plan.get("schema") != "starter/cloudflare-public-delivery/v3":
        raise SystemExit("single-site migration requires the v3 plan")
    architecture = migration_plan.get("architecture", {})
    if architecture.get("topology") != "single-site-multi-repository" or architecture.get("expected_active_worker_count") != 1:
        raise SystemExit("the approved topology is one website and one active Worker")
    if architecture.get("public_cutover_authorized") is not True or migration_plan.get("cutover_state") != "verified-cutover":
        raise SystemExit("canonical cutover must follow approval and live verification")
    if migration_plan.get("site", {}).get("provider_state_verified") is not True:
        raise SystemExit("provider state must be verified for canonical cutover")
    if migration_plan.get("status") != "verified-cutover":
        raise SystemExit("migration status must reflect verified cutover")
    if manifest.get("ecosystem", {}).get("public_delivery", {}).get("migration_state") != migration_plan["status"]:
        raise SystemExit("ecosystem and Cloudflare migration state disagree")
    from build_public_site import validate_lock
    validate_lock(json.loads((ROOT / "site/sources.lock.json").read_text()))

    public_delivery = ecosystem.get("public_delivery")
    if not isinstance(public_delivery, dict):
        raise SystemExit("Starter ecosystem is missing public_delivery")
    if public_delivery.get("current_provider") != "cloudflare-workers" or public_delivery.get("preferred_provider") != "cloudflare-workers":
        raise SystemExit("Starter ecosystem has inconsistent public delivery provider state")

    descriptor = json.loads((ROOT / "docs/agent/entry.json").read_text(encoding="utf-8"))
    if descriptor.get("public_landing") != MACHINE_ENTRY:
        raise SystemExit("agent entry descriptor has the wrong public landing")
    if descriptor.get("human_entry") != HUMAN_ENTRY:
        raise SystemExit("agent entry descriptor has the wrong human entry")
    descriptor_delivery = descriptor.get("public_delivery")
    if not isinstance(descriptor_delivery, dict) or descriptor_delivery.get("preferred_provider") != "cloudflare-workers":
        raise SystemExit("agent entry descriptor must expose Cloudflare Workers as preferred delivery")
    if descriptor_delivery.get("current_provider") != "cloudflare-workers":
        raise SystemExit("agent entry descriptor must identify the approved Worker")
    if descriptor_delivery.get("migration_state") != migration_plan["status"]:
        raise SystemExit("machine entry and Cloudflare migration state disagree")

    agent_page = (ROOT / "docs/agent/index.html").read_text(encoding="utf-8")
    for marker in ("Agent Retrieval Contract", "ecosystem.yaml", "bootstrap.txt", HUMAN_ENTRY):
        if marker not in agent_page:
            raise SystemExit(f"machine-entry page is missing {marker}")

    root_page = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    if MACHINE_ENTRY not in root_page:
        raise SystemExit("Starter homepage does not expose the public machine entry")
    if '<main id="zh" class="lang active">' not in root_page:
        raise SystemExit("Starter homepage must keep Chinese visible as a no-JavaScript fallback")
    required_homepage_markers = [
        "template_source_commit",
        "project_adopted_commit",
        "adoption_state",
        "为什么它不是第四套规范",
    ]
    for marker in required_homepage_markers:
        if marker not in root_page:
            raise SystemExit(f"Starter homepage is missing required architecture marker: {marker}")

    scripts = re.findall(r"<script>(.*?)</script>", root_page, flags=re.DOTALL)
    if not scripts:
        raise SystemExit("Starter homepage has no inline script to validate")
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".js", delete=False) as handle:
        handle.write("\n".join(scripts))
        script_path = handle.name
    try:
        check = subprocess.run(["node", "--check", script_path], capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise SystemExit("Node.js is required to validate Starter homepage JavaScript") from exc
    finally:
        Path(script_path).unlink(missing_ok=True)
    if check.returncode != 0:
        raise SystemExit("Starter homepage JavaScript syntax error:\n" + check.stderr)

    print("ecosystem + machine-entry + homepage + single-site plan validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
