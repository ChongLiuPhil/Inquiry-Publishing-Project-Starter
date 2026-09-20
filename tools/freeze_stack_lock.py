#!/usr/bin/env python3
import argparse, re
from pathlib import Path
import yaml

SHA_RE=re.compile(r"^[0-9a-f]{40}$")
ROLE_LOCK=(("governance","ahicp"),("publishing","ppf"),("portfolio_interface","vault_interface"))

def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",default=str(Path(__file__).resolve().parents[1])); a=p.parse_args()
    root=Path(a.root).resolve()
    stack=yaml.safe_load((root/"project-stack.yaml").read_text(encoding="utf-8"))
    starter=stack["starter"]["adopted_commit"]
    if not SHA_RE.fullmatch(starter or ""):
        raise SystemExit("ERROR: starter.adopted_commit must be the real Starter source commit before freezing")
    resolved={}
    comps=stack.get("components",{})
    for role,lock_key in ROLE_LOCK:
        data=comps.get(role)
        if not data or data.get("adoption_state")!="active":
            resolved[lock_key]=None
        else:
            rev=data.get("template_source_commit")
            if not SHA_RE.fullmatch(rev or ""):
                raise SystemExit(f"ERROR: active component {role} lacks a valid template_source_commit")
            resolved[lock_key]=rev
    resolved["starter"]=starter
    lock={"schema":"inquiry-publishing-stack-lock/v2","generated":True,"resolved":resolved}
    (root/"project-stack.lock.yaml").write_text(yaml.safe_dump(lock,sort_keys=False,allow_unicode=True),encoding="utf-8")
    print("Wrote project-stack.lock.yaml from declared upstream source revisions.")
if __name__=="__main__": main()
