#!/usr/bin/env python3
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
stack = yaml.safe_load((ROOT / "project-stack.yaml").read_text(encoding="utf-8"))
try:
    starter = subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()
except Exception:
    starter = "UNRESOLVED"

components = stack["components"]
lock = {
    "schema": "inquiry-publishing-stack-lock/v1",
    "generated": True,
    "resolved": {
        "ahicp": components["governance"]["adopted_commit"],
        "ppf": components["publishing"]["adopted_commit"],
        "vault_interface": components["portfolio_interface"]["adopted_commit"],
        "starter": starter,
    },
}
(ROOT / "project-stack.lock.yaml").write_text(
    yaml.safe_dump(lock, sort_keys=False, allow_unicode=True), encoding="utf-8"
)
print("Wrote project-stack.lock.yaml")
