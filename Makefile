.DEFAULT_GOAL := all
sources = dirty_equals tests

.PHONY: install
install:
	pip install -U pip pre-commit pip-tools
	pip install -r requirements/all.txt
	pre-commit install

.PHONY: refresh-lockfiles
refresh-lockfiles:
	@echo "Replacing requirements/*.txt files using pip-compile"
	find requirements/ -name '*.txt' ! -name 'all.txt' -type f -delete
	make update-lockfiles

.PHONY: update-lockfiles
update-lockfiles:
	@echo "Updating requirements/*.txt files using pip-compile"
	pip-compile -q -o requirements/linting.txt requirements/linting.in
	pip-compile -q -o requirements/tests.txt -c requirements/linting.txt requirements/tests.in
	pip-compile -q -o requirements/docs.txt -c requirements/linting.txt -c requirements/tests.txt requirements/docs.in
	pip-compile -q -o requirements/pyproject.txt \
		--extra pydantic \
		-c requirements/linting.txt -c requirements/tests.txt -c requirements/docs.txt \
		pyproject.toml
	pip install --dry-run -r requirements/all.txt

.PHONY: format
format:
	ruff check --fix-only $(sources)
	ruff format $(sources)

.PHONY: lint
lint:
	ruff check $(sources)
	ruff format --check $(sources)

.PHONY: test
test:
	TZ=utc coverage run -m pytest
	python tests/mypy_checks.py

.PHONY: testcov
testcov: test
	@coverage report --show-missing
	@coverage html

.PHONY: mypy
mypy:
	mypy dirty_equals tests/mypy_checks.py

.PHONY: docs
docs:
	mkdocs build --strict

.PHONY: all
all: lint mypy testcov docs

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
