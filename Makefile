.PHONY: stack-check stack-doctor stack-test upstream-check adoption-plan

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
