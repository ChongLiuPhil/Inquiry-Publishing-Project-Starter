import copy
from pathlib import Path
import tempfile
import unittest

import yaml

from tools.project_provisioning import (
    PLATFORM_SCHEMA,
    REQUEST_SCHEMA,
    build_plan,
    load_yaml,
    platform_errors,
    validate,
)


ROOT = Path(__file__).resolve().parents[1]


class ProjectProvisioningContractTests(unittest.TestCase):
    def setUp(self):
        self.platform = load_yaml(ROOT / "templates/platform-authorization.yaml")
        self.request = load_yaml(ROOT / "templates/project-provisioning-request.yaml")

    def advanced_request(self):
        request = copy.deepcopy(self.request)
        request["infrastructure"]["profile"] = "agent-provisioned-external-ci"
        request["infrastructure"]["cloudflare"]["access_mode"] = "account-wide-access"
        request["authorization"]["restricted_deployment_source"] = "platform-standing-authorization"
        request["authorization"]["project_bootstrap"] = "platform-automated"
        return request

    def ready_platform(self, request=None):
        request = request or self.advanced_request()
        item = copy.deepcopy(self.platform)
        item["status"] = "ready"
        item["github"].update(
            owner_scope=request["infrastructure"]["github"]["owner"],
            principal_ref="github-user-authorized-provisioner",
            principal_type="github-app-user-access",
            authorization_state="authorized",
        )
        item["cloudflare"].update(
            account_ref="cloudflare-account-ref",
            principal_ref="cloudflare-provisioner-ref",
            authorization_state="authorized",
            all_workers_access="verified",
            worker_creation_authority="authorized",
        )
        item["secret_broker"].update(
            implementation_ref="trusted-broker-ref",
            state="verified",
            plaintext_boundary="verified",
            token_minting_authority="isolated-authorized",
        )
        item["standing_authorizations"].update(
            create_private_repositories=True,
            create_restricted_workers=True,
            restricted_web_deployment=True,
        )
        return item

    def test_templates_validate(self):
        validate(self.platform, PLATFORM_SCHEMA, "platform")
        validate(self.request, REQUEST_SCHEMA, "request")

    def test_default_native_profile_does_not_require_platform_bootstrap(self):
        self.assertEqual(platform_errors(self.platform, self.request), [])
        plan = build_plan(self.platform, self.request)
        self.assertEqual(plan["status"], "READY_FOR_PROJECT_BOOTSTRAP")
        self.assertEqual(plan["infrastructure_profile"], "workers-builds-native")
        self.assertEqual(plan["project_bootstrap"], "human-assisted-once-per-project")

        seed = plan["ppf_handoff"]["desired_state_seed"]
        self.assertEqual(seed["schemaVersion"], 2)
        self.assertEqual(seed["github"]["owner"], "ChongLiuPhil")
        self.assertEqual(seed["github"]["ownerType"], "user")
        self.assertEqual(seed["github"]["repositoryVisibility"], "private")
        self.assertEqual(seed["cloudflare"]["accessMode"], "worker-scoped-access")
        self.assertEqual(seed["cloudflare"]["applicationVisibility"], "private")
        self.assertEqual(seed["deployment"]["provider"], "cloudflare-workers-builds")
        self.assertEqual(seed["deployment"]["securityProfile"], "workers-builds-native")
        self.assertEqual(seed["deployment"]["credentialStrategy"], "provider-managed-user-token")
        self.assertFalse(seed["deployment"]["secretBroker"])
        self.assertFalse(seed["deployment"]["previewDeployments"])

        self.assertIn("connect-repository-to-cloudflare-workers-builds", plan["human_bootstrap_steps"])
        self.assertIn(
            "verify-second-push-auto-deploys-without-reauthorization",
            plan["human_bootstrap_steps"],
        )
        self.assertTrue(
            any("second source push" in item for item in plan["completion_evidence"])
        )

    def test_native_profile_requires_explicit_project_authorization(self):
        request = copy.deepcopy(self.request)
        request["authorization"]["restricted_deployment_source"] = "platform-standing-authorization"
        errors = platform_errors(self.platform, request)
        self.assertIn("NATIVE_PROFILE_REQUIRES_EXPLICIT_PROJECT_AUTHORIZATION", errors)

    def test_native_profile_does_not_require_secret_broker(self):
        platform = copy.deepcopy(self.platform)
        platform["secret_broker"]["state"] = "unverified"
        plan = build_plan(platform, self.request)
        self.assertEqual(plan["status"], "READY_FOR_PROJECT_BOOTSTRAP")
        self.assertFalse(plan["ppf_handoff"]["desired_state_seed"]["deployment"]["secretBroker"])

    def test_advanced_external_ci_requires_platform_bootstrap(self):
        request = self.advanced_request()
        errors = platform_errors(self.platform, request)
        self.assertIn("PLATFORM_AUTHORIZATION_NOT_READY", errors)
        self.assertIn("ACCOUNT_WIDE_ACCESS_NOT_VERIFIED", errors)
        self.assertIn("SECRET_BROKER_NOT_VERIFIED", errors)
        plan = build_plan(self.platform, request)
        self.assertEqual(plan["status"], "BLOCKED")

    def test_ready_platform_yields_advanced_external_ci_handoff(self):
        request = self.advanced_request()
        platform = self.ready_platform(request)
        plan = build_plan(platform, request)
        self.assertEqual(plan["status"], "READY_FOR_PROVISIONER")
        self.assertEqual(plan["infrastructure_profile"], "agent-provisioned-external-ci")
        self.assertEqual(plan["human_bootstrap_steps"], [])
        seed = plan["ppf_handoff"]["desired_state_seed"]
        self.assertEqual(seed["github"]["owner"], "ChongLiuPhil")
        self.assertEqual(seed["github"]["ownerType"], "user")
        self.assertEqual(seed["cloudflare"]["accessMode"], "account-wide-access")
        self.assertEqual(seed["deployment"]["provider"], "github-actions-cloudflare-workers")
        self.assertEqual(seed["deployment"]["credentialStrategy"], "project-scoped-account-token")
        self.assertTrue(seed["deployment"]["secretBroker"])

    def test_broker_minting_authority_must_be_isolated_for_advanced_profile(self):
        request = self.advanced_request()
        platform = self.ready_platform(request)
        platform["secret_broker"]["token_minting_authority"] = "unverified"
        errors = platform_errors(platform, request)
        self.assertIn("SECRET_BROKER_TOKEN_MINTING_AUTHORITY_NOT_ISOLATED", errors)

    def test_personal_owner_rejects_installation_only_principal_for_advanced_profile(self):
        request = self.advanced_request()
        platform = self.ready_platform(request)
        platform["github"]["principal_type"] = "github-app-installation"
        errors = platform_errors(platform, request)
        self.assertIn("GITHUB_USER_REPOSITORY_REQUIRES_USER_ACCESS_OR_CONNECTOR", errors)

    def test_owner_scope_mismatch_blocks_advanced_profile(self):
        request = self.advanced_request()
        platform = self.ready_platform(request)
        platform["github"]["owner_scope"] = "different-owner"
        errors = platform_errors(platform, request)
        self.assertIn("GITHUB_OWNER_OUTSIDE_APPROVED_SCOPE", errors)

    def test_source_public_and_permission_expansion_remain_human_reserved(self):
        platform = self.ready_platform()
        for key in (
            "source_repository_public",
            "provider_permission_scope_expansion",
            "direct_secret_input",
        ):
            platform["standing_authorizations"][key] = True
            with self.subTest(key=key):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "platform.yaml"
                    path.write_text(yaml.safe_dump(platform), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        validate(load_yaml(path), PLATFORM_SCHEMA, "platform")
            platform["standing_authorizations"][key] = False

    def test_public_release_cannot_be_platform_standing_authority(self):
        platform = self.ready_platform()
        platform["standing_authorizations"]["public_release"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "platform.yaml"
            path.write_text(yaml.safe_dump(platform), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(load_yaml(path), PLATFORM_SCHEMA, "platform")


if __name__ == "__main__":
    unittest.main()
