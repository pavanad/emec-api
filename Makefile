.PHONY: help clean lint

.DEFAULT: help

export PYTHONPATH="${PYTHONOCPATH}:$(CURDIR)"

help:
	@echo "\nUsage:"
	@echo "make <command>"
	@echo "\nAvailable Commands:"	
	@echo "- clean\t\t Run clean project"
	@echo "- lint\t\t Check python code against some of the style conventions in PEP 8 and terraform format\n\n"

clean:
	@echo "\n> Run clean project\n";\
	find . -name '*.pyc' -exec rm --force {} +;\
	find . -name '*.pyo' -exec rm --force {} +;\
	find . | grep -E "__pycache__|.pyc" | xargs rm -rf;\
	rm -rf dist/;\

lint:
	@echo "\nRun lint project\n";\
	black . & flake8 .