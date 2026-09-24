import copy
from pathlib import Path
import tempfile
import unittest
import yaml

from tools.project_provisioning import build_plan, load_yaml, platform_errors, validate, PLATFORM_SCHEMA, REQUEST_SCHEMA


ROOT = Path(__file__).resolve().parents[1]


class ProjectProvisioningContractTests(unittest.TestCase):
    def setUp(self):
        self.platform = load_yaml(ROOT / "templates/platform-authorization.yaml")
        self.request = load_yaml(ROOT / "templates/project-provisioning-request.yaml")

    def ready_platform(self):
        item = copy.deepcopy(self.platform)
        item["status"] = "ready"
        item["github"].update(
            owner_scope=self.request["infrastructure"]["github"]["owner"],
            principal_ref="github-app:inquiry-project-provisioner",
            authorization_state="authorized",
        )
        item["cloudflare"].update(
            account_ref="cloudflare-account-ref",
            principal_ref="cloudflare-provisioner-ref",
            authorization_state="authorized",
            all_workers_access="verified",
            worker_creation_authority="authorized",
            token_creation_authority="authorized",
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

    def test_unconfigured_platform_blocks(self):
        errors = platform_errors(self.platform, self.request)
        self.assertIn("PLATFORM_AUTHORIZATION_NOT_READY", errors)
        self.assertIn("ACCOUNT_WIDE_ACCESS_NOT_VERIFIED", errors)

    def test_ready_platform_yields_external_ci_handoff(self):
        platform = self.ready_platform()
        plan = build_plan(platform, self.request)
        self.assertEqual(plan["status"], "READY_FOR_PROVISIONER")
        self.assertEqual(plan["infrastructure_profile"], "agent-provisioned-external-ci")
        seed = plan["ppf_handoff"]["desired_state_seed"]
        self.assertEqual(seed["github"]["repositoryVisibility"], "private")
        self.assertEqual(seed["cloudflare"]["applicationVisibility"], "private")
        self.assertEqual(seed["deployment"]["provider"], "github-actions-cloudflare-workers")
        self.assertEqual(seed["deployment"]["credentialStrategy"], "project-scoped-account-token")
        self.assertTrue(seed["deployment"]["secretBroker"])
        self.assertFalse(seed["release"]["openSource"])
        self.assertIn("public-release", plan["human_reserved_gates"])

    def test_broker_minting_authority_must_be_isolated(self):
        platform = self.ready_platform()
        platform["secret_broker"]["token_minting_authority"] = "unverified"
        errors = platform_errors(platform, self.request)
        self.assertIn("SECRET_BROKER_TOKEN_MINTING_AUTHORITY_NOT_ISOLATED", errors)

    def test_owner_scope_mismatch_blocks(self):
        platform = self.ready_platform()
        platform["github"]["owner_scope"] = "different-owner"
        errors = platform_errors(platform, self.request)
        self.assertIn("GITHUB_OWNER_OUTSIDE_APPROVED_SCOPE", errors)

    def test_public_release_cannot_be_platform_standing_authority(self):
        platform = self.ready_platform()
        platform["standing_authorizations"]["public_release"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "platform.yaml"
            path.write_text(yaml.safe_dump(platform), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(load_yaml(path), PLATFORM_SCHEMA, "platform")

    def test_native_profile_remains_available_but_not_default(self):
        platform = self.ready_platform()
        request = copy.deepcopy(self.request)
        request["infrastructure"]["profile"] = "workers-builds-native"
        plan = build_plan(platform, request)
        self.assertEqual(plan["status"], "READY_FOR_PROVISIONER")
        seed = plan["ppf_handoff"]["desired_state_seed"]
        self.assertEqual(seed["deployment"]["provider"], "cloudflare-workers-builds")
        self.assertEqual(seed["deployment"]["securityProfile"], "workers-builds-native")


if __name__ == "__main__":
    unittest.main()
