.PHONY: stack-check stack-doctor adoption-plan

stack-check:
	python3 tools/stack.py check

stack-doctor:
	python3 tools/stack.py doctor

adoption-plan:
	python3 tools/stack.py adoption-plan
