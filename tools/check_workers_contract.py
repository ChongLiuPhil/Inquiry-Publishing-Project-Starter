#!/usr/bin/env python3
"""Verify that repository delivery configuration preserves approval boundaries."""
import json
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
def main():
    config = json.loads((ROOT / 'wrangler.jsonc').read_text())
    builds = yaml.safe_load((ROOT / 'cloudflare-builds.yaml').read_text())
    plan = yaml.safe_load((ROOT / 'templates/cloudflare-public-delivery.yaml').read_text())
    package = json.loads((ROOT / 'package.json').read_text())
    lock = json.loads((ROOT / 'package-lock.json').read_text())
    checks = [
        (config.get("main") == "src/worker.mjs" and config["assets"].get("binding") == "ASSETS", "Webhook runtime binding missing"),
        (config["assets"].get("run_worker_first") == ["/_events/*"], "Only webhook paths may invoke Worker first"),
        (config.get("keep_vars") is True, "Preserve provider-side App ID"),
        (config['name'] == builds['worker']['name'] == plan['site']['worker_name'] == 'inquirystack', 'Worker name drift'),
        (config['assets']['directory'] == builds['worker']['static_assets_directory'] == './_site', 'Output directory drift'),
        (config['preview_urls'] is False and builds['git']['non_production_branch_builds'] is False, 'Preview needs separately reviewed Access activation'),
        (config['workers_dev'] is True, 'Approved main address must be enabled'),
        (builds['publication']['main_anonymous_reading_authorized'] is True, 'Main reading approval missing'),
        (builds['publication']['canonical_url_cutover_authorized'] is False, 'Canonical cutover not approved'),
        (plan['architecture']['public_cutover_authorized'] is False, 'Formal URL cutover not approved'),
        (builds['commands']['preview_deploy'] == 'npm run cloudflare:preview' and package['scripts']['cloudflare:preview'] == 'wrangler versions upload', 'Preview must not replace main'),
        (lock['packages']['node_modules/wrangler']['version'] == package['devDependencies']['wrangler'] == builds['toolchain']['wrangler'], 'Wrangler lock drift'),
        ((ROOT / '.node-version').read_text().strip() == builds['toolchain']['node'], 'Node pin drift'),
        ((ROOT / '.python-version').read_text().strip() == builds['toolchain']['python'], 'Python pin drift'),
        ('routes' not in config and 'account_id' not in config, 'Do not introduce DNS or private account configuration'),
    ]
    errors = [message for ok, message in checks if not ok]
    if errors:
        raise SystemExit('\n'.join(errors))
    print('PASS: Workers build, toolchain, public-reading and closed-preview boundaries')
if __name__ == '__main__':
    main()
