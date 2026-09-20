.PHONY: stack-check stack-doctor
stack-check:
	python3 tools/stack.py check
stack-doctor:
	python3 tools/stack.py doctor
