from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile

import yaml
from jsonschema import Draft202012Validator


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
        "docs/PROJECT_PROVISIONING_CONTRACT.md",
        "docs/PROJECT_PROVISIONING_CONTRACT.zh-CN.md",
        "docs/PROJECT_PROVISIONING_ACCEPTANCE.md",
        "docs/PROJECT_PROVISIONING_ACCEPTANCE.zh-CN.md",
        "schema/platform-authorization.schema.json",
        "schema/project-provisioning-request.schema.json",
        "templates/platform-authorization.yaml",
        "templates/project-provisioning-request.yaml",
        "project-provisioning.yaml",
    )
    for relative in required_agent_files:
        if not (ROOT / relative).exists():
            raise SystemExit(f"missing public machine-entry artifact: {relative}")

    platform_schema = json.loads((ROOT / "schema/platform-authorization.schema.json").read_text(encoding="utf-8"))
    request_schema = json.loads((ROOT / "schema/project-provisioning-request.schema.json").read_text(encoding="utf-8"))
    platform_template = yaml.safe_load((ROOT / "templates/platform-authorization.yaml").read_text(encoding="utf-8"))
    request_template = yaml.safe_load((ROOT / "templates/project-provisioning-request.yaml").read_text(encoding="utf-8"))
    project_request = yaml.safe_load((ROOT / "project-provisioning.yaml").read_text(encoding="utf-8"))
    for label, instance, schema in (
        ("platform authorization template", platform_template, platform_schema),
        ("project provisioning template", request_template, request_schema),
        ("root project provisioning request", project_request, request_schema),
    ):
        errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: list(e.path))
        if errors:
            where = ".".join(str(x) for x in errors[0].path) or "<root>"
            raise SystemExit(f"{label} is invalid at {where}: {errors[0].message}")
    if platform_template.get("status") != "unconfigured":
        raise SystemExit("public platform-authorization template must not claim live provider authorization")
    standing = platform_template.get("standing_authorizations", {})
    for reserved in ("public_release", "source_repository_public", "reader_audience_expansion", "custom_domain_change", "provider_permission_scope_expansion", "paid_plan_change", "direct_secret_input"):
        if standing.get(reserved) is not False:
            raise SystemExit(f"platform template must keep {reserved} human-reserved")
    broker = platform_template.get("secret_broker", {})
    if broker.get("token_minting_authority") != "unverified":
        raise SystemExit("public platform template must not claim token-minting authority")
    infra = request_template.get("infrastructure", {})
    if infra.get("profile") != "workers-builds-native":
        raise SystemExit("new-project provisioning template must prefer workers-builds-native")
    if infra.get("ci_cost_profile") != "private-project-quota-saver":
        raise SystemExit("new-project provisioning template must prefer private-project-quota-saver")
    github_request = infra.get("github", {})
    if github_request.get("owner") != "ChongLiuPhil" or github_request.get("owner_type") != "user":
        raise SystemExit("new-project provisioning template must default to the ChongLiuPhil personal account")
    if github_request.get("visibility") != "private":
        raise SystemExit("new-project provisioning template must keep GitHub source private")
    cloudflare_request = infra.get("cloudflare", {})
    if cloudflare_request.get("web_visibility") != "restricted" or cloudflare_request.get("preview_enabled") is not False:
        raise SystemExit("new-project provisioning template must default to restricted Web with previews disabled")
    if cloudflare_request.get("access_mode") != "worker-scoped-access":
        raise SystemExit("new-project provisioning template must default to Worker-scoped Access")
    request_authorization = request_template.get("authorization", {})
    if request_authorization.get("restricted_deployment_source") != "explicit-project-authorization":
        raise SystemExit("native default must use explicit per-project restricted-deployment authorization")
    if request_authorization.get("project_bootstrap") != "human-assisted-once-per-project":
        raise SystemExit("native default must use guided per-project bootstrap")
    if request_authorization.get("public_release") is not False:
        raise SystemExit("new-project provisioning template must not pre-authorize public release")
    provisioning = ecosystem.get("project_provisioning")
    if not isinstance(provisioning, dict):
        raise SystemExit("Starter ecosystem is missing project_provisioning")
    if provisioning.get("default_github_owner") != "ChongLiuPhil" or provisioning.get("default_github_owner_type") != "user":
        raise SystemExit("Starter ecosystem must default downstream repositories to the ChongLiuPhil personal account")
    if provisioning.get("default_repository_visibility") != "private":
        raise SystemExit("Starter ecosystem must keep downstream repositories private by default")
    if provisioning.get("preferred_infrastructure_profile") != "workers-builds-native":
        raise SystemExit("Starter ecosystem has the wrong preferred provisioning profile")
    if provisioning.get("default_setup_mode") != "human-assisted-once-per-project":
        raise SystemExit("Starter ecosystem must default to guided per-project bootstrap")
    if provisioning.get("default_access_mode") != "worker-scoped-access":
        raise SystemExit("Starter ecosystem must default to Worker-scoped Access")
    if provisioning.get("default_ci_cost_profile") != "private-project-quota-saver":
        raise SystemExit("Starter ecosystem must default private projects to quota-saver CI")
    if provisioning.get("status") != "guided-per-project-default":
        raise SystemExit("Starter provisioning status must identify the guided per-project default")
    expected_bootstrap_steps = {
        "reuse-existing-cloudflare-git-account-connection-if-available",
        "authorize-cloudflare-github-app-repository-access-if-needed",
        "connect-workers-builds",
        "ensure-worker-application-name-matches-wrangler-jsonc-name",
        "enable-cloudflare-zero-trust-once-if-needed",
        "protect-target-worker-with-access",
        "verify-second-push-auto-deploy-without-reauthorization",
    }
    if not expected_bootstrap_steps.issubset(set(provisioning.get("ordinary_project_human_bootstrap") or [])):
        raise SystemExit("Starter ecosystem is missing current guided-bootstrap prerequisites")
    if provisioning.get("secret_rule") != "provider-credentials-never-enter-model-context":
        raise SystemExit("Starter ecosystem is missing the provider credential secret boundary")
    if provisioning.get("secret_broker_orchestration") != "optional-advanced-ppf-implemented":
        raise SystemExit("Starter ecosystem must expose the optional advanced PPF Secret Broker")
    if provisioning.get("cloudflare_granular_token_issuer") != "optional-advanced-live-acceptance-pending":
        raise SystemExit("advanced Cloudflare granular-token issuer evidence boundary drifted")
    if not str(provisioning.get("trusted_secret_broker_contract", "")).endswith("/docs/TRUSTED_SECRET_BROKER.md"):
        raise SystemExit("Starter ecosystem is missing the PPF Trusted Secret Broker contract")
    reserved = set(provisioning.get("human_reserved") or [])
    required_reserved = {
        "public-release",
        "source-repository-public",
        "reader-audience-expansion",
        "custom-domain-or-dns-authority",
        "provider-permission-scope-expansion",
        "paid-plan-or-billing-change",
        "direct-secret-input-if-trusted-broker-unavailable",
    }
    if not required_reserved.issubset(reserved):
        raise SystemExit("Starter ecosystem is missing one or more human-reserved provisioning gates")

    access_plan_path = ROOT / "templates/cloudflare-access-plan.yaml"
    if not access_plan_path.exists():
        raise SystemExit("missing Cloudflare access plan")
    access_plan = yaml.safe_load(access_plan_path.read_text(encoding="utf-8"))
    if access_plan.get("default_access_mode") != "worker-scoped-access":
        raise SystemExit("Cloudflare access plan must default to Worker-scoped Access")
    project_bootstrap = access_plan.get("project_bootstrap", {})
    if project_bootstrap.get("mode") != "human-assisted-once-per-project":
        raise SystemExit("Cloudflare access plan must use guided per-project bootstrap")
    if project_bootstrap.get("default_path") != "cloudflare-dashboard":
        raise SystemExit("Cloudflare access plan must default to the Dashboard connection path")
    if project_bootstrap.get("requires_api_token") is not False:
        raise SystemExit("default Cloudflare project bootstrap must not require an API token")
    reservations = set(access_plan.get("human_reservations") or [])
    if "first-api-token-creation" in reservations:
        raise SystemExit("Cloudflare access plan must not require API-token creation by default")
    if "api-token-creation-only-if-api-automation-selected" not in reservations:
        raise SystemExit("Cloudflare access plan must make API-token creation conditional on API automation")
    verification = set(access_plan.get("verification") or [])
    if "second-push-auto-deploys-without-reauthorization" not in verification:
        raise SystemExit("Cloudflare access plan must verify second-push automatic deployment")

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
    legacy = migration_plan.get("legacy_entries", {})
    if legacy.get("status") != "retired-2026-09-23" or legacy.get("available") is not False:
        raise SystemExit("retired GitHub Pages entries must not be offered as live rollback paths")
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
    descriptor_provisioning = descriptor.get("project_provisioning")
    if not isinstance(descriptor_provisioning, dict):
        raise SystemExit("agent entry descriptor is missing project_provisioning")
    if descriptor_provisioning.get("default_github_owner") != "ChongLiuPhil" or descriptor_provisioning.get("default_github_owner_type") != "user":
        raise SystemExit("agent entry descriptor must default downstream repositories to the ChongLiuPhil personal account")
    if descriptor_provisioning.get("default_repository_visibility") != "private":
        raise SystemExit("agent entry descriptor must keep downstream repositories private by default")
    if descriptor_provisioning.get("preferred_profile") != "workers-builds-native":
        raise SystemExit("agent entry descriptor has the wrong provisioning profile")
    if descriptor_provisioning.get("default_setup_mode") != "human-assisted-once-per-project":
        raise SystemExit("agent entry descriptor must expose guided per-project bootstrap")
    if descriptor_provisioning.get("default_access_mode") != "worker-scoped-access":
        raise SystemExit("agent entry descriptor must expose Worker-scoped Access")
    if descriptor_provisioning.get("default_ci_cost_profile") != "private-project-quota-saver":
        raise SystemExit("agent entry descriptor must expose private-project-quota-saver")
    action_policy = descriptor_provisioning.get("private_project_github_actions") or {}
    expected_action_policy = {
        "content_only_changes": "none",
        "configuration_pull_request": "light-contract-check",
        "main_push": "none",
        "heavy_validation": "manual",
    }
    if action_policy != expected_action_policy:
        raise SystemExit("agent entry descriptor has the wrong private-project GitHub Actions policy")
    if not str(descriptor_provisioning.get("ci_cost_policy", "")).endswith("/docs/CI_COST_POLICY.md"):
        raise SystemExit("agent entry descriptor is missing the PPF CI cost policy")
    if descriptor_provisioning.get("status") != "guided-per-project-default":
        raise SystemExit("agent entry descriptor must identify the guided per-project default")
    if not expected_bootstrap_steps.issubset(set(descriptor_provisioning.get("ordinary_project_human_bootstrap") or [])):
        raise SystemExit("agent entry descriptor is missing current guided-bootstrap prerequisites")
    if descriptor_provisioning.get("secret_broker_required_for_default") is not False:
        raise SystemExit("native default must not require the trusted Secret Broker")
    if descriptor_provisioning.get("secret_broker_orchestration") != "optional-advanced-ppf-implemented":
        raise SystemExit("agent entry descriptor must expose the optional advanced PPF Secret Broker")
    if descriptor_provisioning.get("cloudflare_granular_token_issuer") != "optional-advanced-live-acceptance-pending":
        raise SystemExit("agent entry descriptor must preserve the advanced token-issuer evidence boundary")
    if not str(descriptor_provisioning.get("trusted_secret_broker_contract", "")).endswith("/docs/TRUSTED_SECRET_BROKER.md"):
        raise SystemExit("agent entry descriptor is missing the PPF Trusted Secret Broker contract")
    descriptor_reserved = set(descriptor_provisioning.get("human_reserved_gates") or [])
    if not {
        "public-release",
        "source-repository-public",
        "reader-audience-expansion",
        "custom-domain-or-dns-authority",
        "provider-permission-scope-expansion",
        "paid-plan-or-billing-change",
        "direct-secret-input-if-trusted-broker-unavailable",
    }.issubset(descriptor_reserved):
        raise SystemExit("agent entry descriptor is missing human-reserved provisioning gates")
    if descriptor.get("authorization", {}).get("public_release_requires_separate_human_approval") is not True:
        raise SystemExit("machine entry must preserve separate human public-release approval")
    if descriptor.get("authorization", {}).get("deployment_token_plaintext_in_model_context") is not False:
        raise SystemExit("machine entry must prohibit deployment-token plaintext in model context")

    contract_en = (ROOT / "docs/PROJECT_PROVISIONING_CONTRACT.md").read_text(encoding="utf-8")
    contract_zh = (ROOT / "docs/PROJECT_PROVISIONING_CONTRACT.zh-CN.md").read_text(encoding="utf-8")
    acceptance_en = (ROOT / "docs/PROJECT_PROVISIONING_ACCEPTANCE.md").read_text(encoding="utf-8")
    acceptance_zh = (ROOT / "docs/PROJECT_PROVISIONING_ACCEPTANCE.zh-CN.md").read_text(encoding="utf-8")
    for label, text_value, required_values in (
        ("English provisioning contract", contract_en, ("wrangler.jsonc.name", "Zero Trust", "Git-account connection", "private-project-quota-saver", "content-only", "Cloudflare Workers Builds")),
        ("English provisioning acceptance", acceptance_en, ("wrangler.jsonc.name", "Zero Trust", "Git-account connection", "private-project-quota-saver", "content-only", "production Web build")),
        ("Chinese provisioning contract", contract_zh, ("wrangler.jsonc.name", "Zero Trust", "Git account", "private-project-quota-saver", "content-only", "Cloudflare Workers Builds")),
        ("Chinese provisioning acceptance", acceptance_zh, ("wrangler.jsonc.name", "Zero Trust", "Git account", "private-project-quota-saver", "content-only", "production Web build")),
    ):
        for required in required_values:
            if required not in text_value:
                raise SystemExit(f"{label} is missing current Cloudflare prerequisite: {required}")

    retrieval_en = (ROOT / "docs/AGENT_RETRIEVAL_CONTRACT.md").read_text(encoding="utf-8")
    retrieval_zh = (ROOT / "docs/AGENT_RETRIEVAL_CONTRACT.zh-CN.md").read_text(encoding="utf-8")
    for required in (
        "workers-builds-native",
        "private-project-quota-saver",
        "content-only",
        "human-assisted-once-per-project",
        "worker-scoped-access",
        "second push",
        "optional advanced profile",
    ):
        if required not in retrieval_en:
            raise SystemExit(f"English Agent Retrieval Contract is missing guided-default marker: {required}")
    for required in (
        "workers-builds-native",
        "private-project-quota-saver",
        "content-only",
        "human-assisted-once-per-project",
        "worker-scoped-access",
        "第二次 push",
        "高级可选 Profile",
    ):
        if required not in retrieval_zh:
            raise SystemExit(f"Chinese Agent Retrieval Contract is missing guided-default marker: {required}")
    if "preferred infrastructure profile after platform bootstrap is `agent-provisioned-external-ci`" in retrieval_en:
        raise SystemExit("English Agent Retrieval Contract still prefers external CI by default")
    if "平台 bootstrap 完成后，首选 infrastructure profile 为 `agent-provisioned-external-ci`" in retrieval_zh:
        raise SystemExit("Chinese Agent Retrieval Contract still prefers external CI by default")

    agent_page = (ROOT / "docs/agent/index.html").read_text(encoding="utf-8")
    for marker in ("Agent Retrieval Contract", "Project Provisioning", "workers-builds-native", "private-project-quota-saver", "human-assisted-once-per-project", "ecosystem.yaml", "bootstrap.txt", HUMAN_ENTRY):
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
        "workers-builds-native",
        "private-project-quota-saver",
        "每项目一次配置",
        "第二次 push",
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

    print("ecosystem + provisioning + machine-entry + homepage + single-site plan validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
