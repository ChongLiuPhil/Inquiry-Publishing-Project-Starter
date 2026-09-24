.PHONY: stack-check stack-doctor stack-test upstream-check adoption-plan provisioning-contract-check provisioning-plan

stack-check:
	python3 tools/stack.py check

stack-doctor:
	python3 tools/stack.py doctor

stack-test:
	python3 -m unittest discover -s tests -v

upstream-check:
	python3 tools/check_upstream_contracts.py

adoption-plan:
	python3 tools/stack.py adoption-plan

provisioning-contract-check:
	python3 tools/project_provisioning.py validate

provisioning-plan:
	python3 tools/project_provisioning.py plan --json
