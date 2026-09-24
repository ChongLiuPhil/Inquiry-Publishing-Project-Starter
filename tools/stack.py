#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

CATALOG_ROOT = Path(__file__).resolve().parents[1]
ROLE_TO_SOURCE = {"governance":"ahicp","publishing":"ppf","portfolio_interface":"vault-interface"}
LOCK_KEYS = {"governance":"ahicp","publishing":"ppf","portfolio_interface":"vault_interface"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

def load(root, path):
    p = root / path
    if not p.is_file(): raise SystemExit(f"ERROR: missing {p}")
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def load_json(root, path):
    return json.loads((root / path).read_text(encoding="utf-8"))

def validate_schema(instance, schema_path, label):
    v=Draft202012Validator(load_json(CATALOG_ROOT, schema_path))
    errors=sorted(v.iter_errors(instance), key=lambda e:list(e.path))
    if errors:
        for e in errors:
            where=".".join(str(x) for x in e.path) or "<root>"
            print(f"ERROR {label} {where}: {e.message}", file=sys.stderr)
        return False
    return True

def profile_def(name):
    return load(CATALOG_ROOT, f"profiles/{name}.yaml")

def source_map():
    return load(CATALOG_ROOT, "stack/source-map.yaml")

def stack_errors(root):
    stack=load(root,"project-stack.yaml"); lock=load(root,"project-stack.lock.yaml")
    ok1=validate_schema(stack,"schema/project-stack.schema.json","project-stack")
    ok2=validate_schema(lock,"schema/project-stack-lock.schema.json","project-stack.lock")
    if not (ok1 and ok2): return ["schema validation failed"]
    errors=[]
    profile=profile_def(stack["profile"])
    if stack["starter"]["profile"] != stack["profile"]:
        errors.append("starter.profile must equal stack profile")

    provisioning_path=root/"project-provisioning.yaml"
    provisioning_meta=stack["starter"].get("project_provisioning")
    if provisioning_path.is_file():
        provisioning=load(root,"project-provisioning.yaml")
        if not validate_schema(provisioning,"schema/project-provisioning-request.schema.json","project-provisioning"):
            errors.append("project provisioning schema validation failed")
        else:
            if provisioning.get("project",{}).get("id") != stack["project"]["id"]:
                errors.append("project-provisioning.yaml project id differs from stack project id")
            if provisioning.get("stack_profile") != stack["profile"]:
                errors.append("project-provisioning.yaml stack_profile differs from project-stack profile")
            if not provisioning_meta:
                errors.append("starter.project_provisioning is required when project-provisioning.yaml exists")
            elif provisioning_meta.get("profile") != provisioning.get("infrastructure",{}).get("profile"):
                errors.append("starter.project_provisioning.profile differs from project-provisioning.yaml infrastructure.profile")
            elif provisioning_meta.get("request_ref") != "project-provisioning.yaml":
                errors.append("starter.project_provisioning.request_ref must point to project-provisioning.yaml")
    elif provisioning_meta:
        errors.append("project-provisioning.yaml is missing while starter.project_provisioning is configured")
    required=set(profile.get("required_components",[])); optional=set(profile.get("optional_components",[]))
    requested=required|optional
    components=stack.get("components",{}); resolved=lock["resolved"]; sm=source_map()["sources"]

    for role, source_key in ROLE_TO_SOURCE.items():
        data=components.get(role); state=(data or {}).get("adoption_state")
        if source_key in required and state != "active":
            errors.append(f"{source_key} is required by profile {stack['profile']} and must be active")
        if source_key not in requested and state == "active":
            errors.append(f"{source_key} is not part of profile {stack['profile']} but is active")
        if source_key in optional and data is not None and state not in {"active","deferred","not-applicable"}:
            errors.append(f"{source_key} optional component has invalid state")
        if data:
            if data.get("source") != sm[source_key]["repository"]:
                errors.append(f"{source_key} source differs from source-map repository")
            lk=LOCK_KEYS[role]
            if state=="active":
                rev=data.get("template_source_commit")
                if resolved.get(lk) != rev: errors.append(f"lock drift: {lk} != template_source_commit")
            elif state in {"deferred","not-applicable"} and resolved.get(lk) is not None:
                errors.append(f"{lk} lock must be null while component is {state}")
        elif source_key in required:
            errors.append(f"missing required component: {role}")

    starter_rev=stack["starter"]["adopted_commit"]
    if resolved.get("starter") != starter_rev:
        errors.append("lock drift: starter != starter.adopted_commit")
    if lock.get("generated") is True and not SHA_RE.fullmatch(starter_rev or ""):
        errors.append("generated lock requires a real Starter source commit")

    project_path=root/"project.yaml"; website_path=root/"website.yaml"; publishing_path=root/"publishing.yaml"
    if project_path.is_file() and website_path.is_file():
        project=load(root,"project.yaml"); website=load(root,"website.yaml"); pid=stack["project"]["id"]
        if project.get("id") != pid: errors.append("project.yaml id differs from stack project id")
        if website.get("project_id") != pid: errors.append("website.yaml project_id differs from stack project id")
    pub=components.get("publishing")
    if publishing_path.is_file() and pub and pub.get("adoption_state")=="active":
        publishing=load(root,"publishing.yaml"); pid=stack["project"]["id"]
        if publishing.get("project",{}).get("id") != pid: errors.append("publishing.yaml project id differs from stack project id")
        web=publishing.get("publication",{}).get("web",{}); dep=publishing.get("deployment",{}).get("web",{})
        if web.get("authorization_state") != "authorized" and dep.get("enabled") is True:
            errors.append("deployment cannot be enabled before publication authorization")
        if website_path.is_file():
            website=load(root,"website.yaml")
            if website.get("publish") is True and web.get("authorization_state") != "authorized":
                errors.append("website.publish=true requires Web publication authorization")
    return errors

def check(root):
    errors=stack_errors(root)
    if errors:
        for e in errors: print("ERROR:",e,file=sys.stderr)
        raise SystemExit(1)
    print("Stack consistency check passed.")

def doctor(root):
    stack=load(root,"project-stack.yaml")
    print("profile:",stack.get("profile"))
    for name,data in stack.get("components",{}).items():
        print(f"{name}: {data.get('adoption_state')} {data.get('source')} @ {data.get('template_source_commit')}")
    try: check(root)
    except SystemExit:
        print("stack health: DRIFTED"); raise
    print("stack health: CONSISTENT")

def build_adoption_plan(root):
    stack=load(root,"project-stack.yaml"); sm=source_map()
    plan={"schema":"inquiry-publishing-adoption-plan/v2","project_id":stack["project"]["id"],"profile":stack["profile"],
          "components":[],"ownership":{"policy":"read-from-pinned-upstream-manifests","starter_contract":"stack/managed-paths.yaml"},
          "project_provisioning":stack.get("starter",{}).get("project_provisioning"),
          "rules":["fresh-read each pinned upstream manifest before write","never overwrite upstream-declared project-owned paths automatically",
                   "three-way compare upstream-declared merge-managed paths","preserve human approvals and provider actual state",
                   "validate project-provisioning.yaml before invoking the PPF provisioner",
                   "apply through branch/PR and run project-local gates"]}
    for role,source_key in ROLE_TO_SOURCE.items():
        data=stack.get("components",{}).get(role)
        if not data: continue
        src=sm["sources"][source_key]; state=data["adoption_state"]
        item={"role":role,"framework":data["framework"],"repository":data["source"],"adoption_state":state,
              "template_source_revision":data.get("template_source_commit"),"project_adopted_revision":data.get("project_adopted_commit")}
        if state=="active":
            item.update({"template_root":src["template_root"],"manifest_path":src["manifest_path"],"adoption_mode":src["adoption_mode"],
                         "ownership_source":f"{data['source']}@{data['template_source_commit']}:{src['manifest_path']}"})
        plan["components"].append(item)
    return plan

def adoption_plan(root, as_json=False):
    plan=build_adoption_plan(root)
    if as_json: print(json.dumps(plan,indent=2,ensure_ascii=False)); return
    print(f"project: {plan['project_id']}"); print(f"profile: {plan['profile']}")
    for c in plan["components"]:
        print(f"- {c['role']}: {c['adoption_state']} {c['repository']} @ {c['template_source_revision']}")
        if c.get("ownership_source"): print(f"  ownership_source: {c['ownership_source']}")
    if plan.get("project_provisioning"):
        print(f"provisioning: {plan['project_provisioning'].get('profile')} via {plan['project_provisioning'].get('request_ref')}")
    print("rule: ownership classes come from pinned upstream manifests, not a copied aggregate list")

def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["check","doctor","adoption-plan"]); p.add_argument("--json",action="store_true")
    p.add_argument("--root",default=str(CATALOG_ROOT)); a=p.parse_args(); root=Path(a.root).resolve()
    if a.command=="check": check(root)
    elif a.command=="doctor": doctor(root)
    else: adoption_plan(root,a.json)
if __name__=="__main__": main()
