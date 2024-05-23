.PHONY: help clean lint build publish

.DEFAULT: help

export PYTHONPATH="${PYTHONOCPATH}:$(CURDIR)"

help:
	@echo "\nUsage:"
	@echo "make <command>"
	@echo "\nAvailable Commands:"
	@echo "- clean\t\t Run clean project."
	@echo "- lint\t\t Check python code against some of the style conventions in PEP 8 and terraform format."
	@echo "- build\t\t Builds a package, as a tarball and a wheel by default."
	@echo "- publish\t Publishes a package to a remote repository.\n\n"


clean:
	@echo "\n> Run clean project\n";\
	find . -name '*.pyc' -exec rm --force {} +;\
	find . -name '*.pyo' -exec rm --force {} +;\
	find . | grep -E "__pycache__|.pyc" | xargs rm -rf;\
	rm -rf dist/;\

lint:
	@echo "\nRun lint project\n";\
	black . & flake8 .

build:
	@echo "\nBuilds a package, as a tarball and a wheel by default.\n";\
	poetry build

publish:
	@echo "\nRun publish package in pypi\n";\
	poetry run twine upload dist/*