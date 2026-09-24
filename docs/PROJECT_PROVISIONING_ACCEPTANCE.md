# Project Provisioning Acceptance

**Purpose:** live end-to-end acceptance for `agent-provisioned-external-ci`.

Repository CI, mocks, and provider API simulations do not satisfy this acceptance.

## Preconditions

- platform authorization is privately recorded and validates as ready;
- account-wide Cloudflare Access protection is verified;
- GitHub and Cloudflare provisioning principals are inside approved scopes;
- trusted secret broker is available;
- the pilot slug has no existing repository or Worker;
- no custom domain, DNS change, or paid product is required.

## Pilot

Use a disposable project slug and no user manuscript or local-computer material.

1. Create a new provisioning request with the default full stack and external-CI profile.
2. Generate and review the Starter provisioning plan.
3. Fresh-read pinned AHICP, PPF, and Vault manifests.
4. Create the private GitHub repository through the authorized provisioning principal.
5. Compose the pinned stack/template into that repository.
6. Re-verify account-wide Access, then create Worker metadata.
7. Confirm the new workers.dev endpoint is not anonymously readable before source deployment.
8. Have the PPF provisioner emit the secret-broker request.
9. Through the trusted broker, discover and verify the current Cloudflare individual-Worker policy encoding, create the account-owned credential, prove through non-secret Provider policy/identity evidence that it targets exactly the intended Worker with `Editor`, and install GitHub Actions secrets without returning plaintext to the Agent.
10. Run repository validation and the deployment workflow.
11. Confirm the intended Git SHA/revision is deployed.
12. Confirm anonymous production access is denied/challenged.
13. If an approved pilot reader exists, verify authorized reading; otherwise do not invent a reader and keep the acceptance limited to anonymous denial.
14. Request at least one generated asset anonymously and confirm it is also denied/challenged.
15. Confirm preview URLs remain disabled. Test previews only as a separate later acceptance.
16. Confirm no secret value appears in repository history, Actions logs, issues, PRs, Agent output, or public metadata.
17. Record non-secret repository ID, Worker ID/name, deployed revision, Access references, verification timestamp, and rollback target in private state.
18. Trigger one later source change and verify deployment succeeds with the same project-scoped credential and no new platform authorization.
19. Re-run with no meaningful source change and confirm no unintended infrastructure drift.
20. Exercise rollback to the previous verified deployment/version and then restore current, verifying restricted access in both states.

## Pass criteria

Acceptance passes only if:

- no per-project platform reauthorization was needed;
- GitHub source remained private;
- account-wide Access stayed enabled;
- the minted Cloudflare credential's actual Provider policy/identity was recorded as non-secret evidence and limited routine CI authority to exactly the intended Worker with `Editor`;
- token plaintext never entered model/Git/logs;
- deployment and revision verification succeeded;
- anonymous production and direct-asset access were denied/challenged;
- rollback worked;
- no paid-plan, domain, DNS, or public-release change occurred.

## Evidence record

Record project slug, immutable commit IDs, non-secret Worker identity, workflow run IDs, deployed version/revision, HTTP results, Access references, rollback version, exact dates, and any failure/recovery steps.

Do not record token values, private keys, OTPs, reader identities, or account-private secrets.

After a pass, update PPF and Starter from `live-new-project-acceptance-pending` to a dated verified state through a reviewed PR.
