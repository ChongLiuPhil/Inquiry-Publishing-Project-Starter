#!/usr/bin/env python3
"""Validate platform authorization and create a machine-readable new-project provisioning plan."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLATFORM_SCHEMA = ROOT / "schema/platform-authorization.schema.json"
REQUEST_SCHEMA = ROOT / "schema/project-provisioning-request.schema.json"


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def validate(instance: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        rendered = []
        for error in errors:
            where = ".".join(str(part) for part in error.path) or "<root>"
            rendered.append(f"{label}.{where}: {error.message}")
        raise ValueError("\n".join(rendered))


def platform_errors(platform: dict[str, Any], request: dict[str, Any]) -> list[str]:
    """Return only the authorization blockers required by the selected profile.

    Workers Builds Native deliberately permits a short human-assisted bootstrap
    for each project, so it does not require platform standing authorization,
    account-wide Access, or the Trusted Secret Broker.

    The advanced external-CI profile retains the stronger reusable platform
    authorization requirements.
    """
    errors: list[str] = []
    profile = request["infrastructure"]["profile"]
    authorization = request["authorization"]

    if authorization["public_release"] is not False:
        errors.append("PUBLIC_RELEASE_MUST_NOT_BE_PREAUTHORIZED_BY_PROJECT_REQUEST")

    if profile == "workers-builds-native":
        if authorization.get("restricted_deployment_source") != "explicit-project-authorization":
            errors.append("NATIVE_PROFILE_REQUIRES_EXPLICIT_PROJECT_AUTHORIZATION")
        if authorization.get("project_bootstrap") != "human-assisted-once-per-project":
            errors.append("NATIVE_PROFILE_REQUIRES_GUIDED_PROJECT_BOOTSTRAP")
        return list(dict.fromkeys(errors))

    if authorization.get("project_bootstrap") != "platform-automated":
        errors.append("EXTERNAL_CI_REQUIRES_PLATFORM_AUTOMATED_BOOTSTRAP")

    if platform.get("status") != "ready":
        errors.append("PLATFORM_AUTHORIZATION_NOT_READY")

    github = platform.get("github", {})
    cloudflare = platform.get("cloudflare", {})
    broker = platform.get("secret_broker", {})
    standing = platform.get("standing_authorizations", {})
    req_github = request["infrastructure"]["github"]

    if github.get("authorization_state") != "authorized":
        errors.append("GITHUB_PROVISIONING_PRINCIPAL_NOT_AUTHORIZED")
    if github.get("owner_scope") != req_github.get("owner"):
        errors.append("GITHUB_OWNER_OUTSIDE_APPROVED_SCOPE")
    principal_type = github.get("principal_type")
    if req_github.get("owner_type") == "user" and principal_type == "github-app-installation":
        errors.append("GITHUB_USER_REPOSITORY_REQUIRES_USER_ACCESS_OR_CONNECTOR")
    if principal_type not in {"github-app-user-access", "github-app-installation", "authorized-provider-connector"}:
        errors.append("GITHUB_PROVISIONING_PRINCIPAL_TYPE_NOT_VERIFIED")

    if cloudflare.get("authorization_state") != "authorized":
        errors.append("CLOUDFLARE_PROVISIONING_PRINCIPAL_NOT_AUTHORIZED")
    if cloudflare.get("all_workers_access") != "verified":
        errors.append("ACCOUNT_WIDE_ACCESS_NOT_VERIFIED")
    if cloudflare.get("worker_creation_authority") != "authorized":
        errors.append("WORKER_CREATION_AUTHORITY_NOT_AUTHORIZED")
    if broker.get("state") != "verified":
        errors.append("SECRET_BROKER_NOT_VERIFIED")
    if broker.get("plaintext_boundary") != "verified":
        errors.append("SECRET_BROKER_PLAINTEXT_BOUNDARY_NOT_VERIFIED")
    if broker.get("token_minting_authority") != "isolated-authorized":
        errors.append("SECRET_BROKER_TOKEN_MINTING_AUTHORITY_NOT_ISOLATED")

    for key in (
        "create_private_repositories",
        "create_restricted_workers",
        "restricted_web_deployment",
    ):
        if standing.get(key) is not True:
            errors.append("STANDING_AUTHORIZATION_MISSING_" + key.upper())

    for key in (
        "public_release",
        "source_repository_public",
        "reader_audience_expansion",
        "custom_domain_change",
        "provider_permission_scope_expansion",
        "paid_plan_change",
        "direct_secret_input",
    ):
        if standing.get(key) is not False:
            errors.append("RESERVED_HUMAN_GATE_MUST_REMAIN_FALSE_" + key.upper())

    if authorization["restricted_deployment_source"] == "platform-standing-authorization":
        if standing.get("restricted_web_deployment") is not True:
            errors.append("RESTRICTED_DEPLOYMENT_NOT_COVERED_BY_PLATFORM_AUTHORIZATION")
    return list(dict.fromkeys(errors))

def build_plan(platform: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    errors = platform_errors(platform, request)
    profile = request["infrastructure"]["profile"]
    ci_cost_profile = request["infrastructure"]["ci_cost_profile"]
    guided_native = profile == "workers-builds-native"
    project = request["project"]
    infra = request["infrastructure"]
    authorization = request["authorization"]

    ready_status = "READY_FOR_PROJECT_BOOTSTRAP" if guided_native else "READY_FOR_PROVISIONER"
    access_mode = infra["cloudflare"]["access_mode"]

    completion_evidence = (
        [
            "private GitHub repository exists at intended personal-account identity",
            "Cloudflare Git repository connection points to the intended repository",
            "production branch is main and the production trigger is active",
            "target Worker identity exists",
            "Worker-scoped Access or an explicitly selected verified account-wide Access policy protects the project",
            "first restricted deployment serves the intended source revision",
            "anonymous production access is challenged or denied",
            "direct assets cannot bypass access control",
            "a second source push deploys automatically without renewed GitHub or Cloudflare authorization",
            "content-only changes do not trigger automatic GitHub Actions",
            "main pushes do not duplicate the production Web build in GitHub Actions",
            "non-secret provider state and rollback point are durably recorded",
        ]
        if guided_native
        else [
            "private GitHub repository exists at intended identity",
            "account-wide Access remains verified",
            "target Worker identity exists",
            "project-scoped deployment credential is installed without exposing plaintext",
            "authorized GitHub Actions deployment succeeds",
            "deployed revision matches intended source revision",
            "anonymous production access is challenged or denied",
            "direct assets cannot bypass access control",
            "non-secret provider state and rollback point are durably recorded",
        ]
    )

    plan = {
        "schema": "inquiry-publishing-stack/project-provisioning-plan/v1",
        "status": "BLOCKED" if errors else ready_status,
        "project": project,
        "stack_profile": request["stack_profile"],
        "infrastructure_profile": profile,
        "ci_cost_profile": ci_cost_profile,
        "blockers": errors,
        "authorization_source": authorization["restricted_deployment_source"],
        "project_bootstrap": authorization["project_bootstrap"],
        "component_adoption": {
            "governance": "full-ahicp",
            "publishing": "full-ppf",
            "portfolio_interface": "vault-interface",
            "ownership_policy": "fresh-read-pinned-upstream-manifests",
        },
        "ppf_handoff": {
            "authority": "ChongLiuPhil/Personal-Publishing-Framework",
            "profile": profile,
            "required_contract": (
                "docs/PER_PROJECT_GITHUB_CLOUDFLARE_SETUP.md"
                if guided_native
                else "docs/AGENT_PROVISIONED_EXTERNAL_CI.md"
            ),
            "desired_state_seed": {
                "schemaVersion": 2,
                "project": {"id": project["id"], "slug": infra["github"]["repository"]},
                "github": {
                    "owner": infra["github"]["owner"],
                    "ownerType": infra["github"]["owner_type"],
                    "repository": infra["github"]["repository"],
                    "repositoryVisibility": "private",
                    "productionBranch": "main",
                },
                "cloudflare": {
                    "platform": "workers",
                    "worker": infra["cloudflare"]["worker"],
                    "applicationVisibility": "private",
                    "previewVisibility": "private",
                    "accessMode": access_mode,
                    "publicBypass": False,
                    "customDomain": None,
                },
                "deployment": {
                    "provider": (
                        "cloudflare-workers-builds"
                        if guided_native
                        else "github-actions-cloudflare-workers"
                    ),
                    "productionBranch": "main",
                    "previewDeployments": infra["cloudflare"]["preview_enabled"],
                    "previewProtection": True,
                    "securityProfile": (
                        "workers-builds-native"
                        if guided_native
                        else "agent-provisioned-external-ci"
                    ),
                    "credentialStrategy": (
                        "provider-managed-user-token"
                        if guided_native
                        else "project-scoped-account-token"
                    ),
                    "secretBroker": not guided_native,
                    "ciCostProfile": ci_cost_profile,
                },
                "release": {"state": "private", "openSource": False},
                "policy": {
                    "privateByDefault": True,
                    "paidServicesAllowed": False,
                    "requiresApprovedPublicTransition": True,
                },
            },
            "validation_rule": "Validate this seed against the PPF schema pinned by the project's adopted PPF template revision before any provider write.",
            "publication_materialization": {
                "source.visibility": "private",
                "publication.web.enabled": True,
                "publication.web.authorization_state": "authorized" if not errors else "not-authorized",
                "publication.web.visibility": "restricted",
                "publication.web.access.mode": "authenticated",
                "publication.web.access.implementation": "cloudflare-access",
                "publication.web.access.policy_ref": "shared-reader-access",
                "deployment.web.integration_mode": (
                    "workers-builds-git"
                    if guided_native
                    else "github-actions-external-ci"
                ),
                "deployment.web.enabled": True if not errors else False,
                "deployment.web.status": "staged",
                "public_release": False,
                "authorization_basis": authorization["restricted_deployment_source"],
            },
        },
        "human_bootstrap_steps": (
            [
                "create-or-confirm-private-personal-github-repository",
                "reuse-existing-cloudflare-git-account-connection-if-available",
                "authorize-cloudflare-github-app-repository-access-if-needed",
                "connect-repository-to-cloudflare-workers-builds",
                "ensure-worker-application-name-matches-wrangler-jsonc-name",
                "enable-cloudflare-zero-trust-once-if-needed",
                "protect-target-worker-with-cloudflare-access",
                "verify-first-restricted-deployment",
                "verify-second-push-auto-deploys-without-reauthorization",
            ]
            if guided_native
            else []
        ),
        "human_reserved_gates": [
            "public-release",
            "source-repository-public",
            "reader-audience-expansion",
            "custom-domain-or-dns-authority",
            "provider-permission-scope-expansion",
            "paid-plan-or-billing-change",
            "direct-secret-input-if-trusted-broker-unavailable",
        ],
        "completion_evidence": completion_evidence,
    }
    return plan

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "check", "plan"))
    parser.add_argument("--platform", type=Path, default=ROOT / "templates/platform-authorization.yaml")
    parser.add_argument("--request", type=Path, default=ROOT / "templates/project-provisioning-request.yaml")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        platform = load_yaml(args.platform)
        request = load_yaml(args.request)
        validate(platform, PLATFORM_SCHEMA, "platform")
        validate(request, REQUEST_SCHEMA, "request")
        if args.command == "validate":
            print("Project provisioning schemas and templates are valid.")
            return 0
        plan = build_plan(platform, request)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "CONFIGURATION_ERROR", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    if args.command == "check":
        if plan["blockers"]:
            print(json.dumps({"status": "BLOCKED", "blockers": plan["blockers"]}, ensure_ascii=False, indent=2))
            return 2
        print("Project provisioning authorization check passed.")
        return 0

    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(f"status: {plan['status']}")
        print(f"project: {plan['project']['id']}")
        print(f"stack profile: {plan['stack_profile']}")
        print(f"infrastructure profile: {plan['infrastructure_profile']}")
        if plan["blockers"]:
            for blocker in plan["blockers"]:
                print(f"blocker: {blocker}")
        else:
            print("next: fresh-read pinned PPF/AHICP/Vault manifests, validate the PPF desired-state seed, then follow the selected PPF setup contract.")
    return 0 if not plan["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
