.DEFAULT_GOAL := all
isort = isort dirty_equals tests
black = black dirty_equals tests

.PHONY: install
install:
	pip install -r requirements/all.txt
	pre-commit install

.PHONY: generate-dependencies-310
generate-dependencies-310:
	python -c 'import sys; sys.exit(sys.version_info[:2] != (3, 10))'
	python -m piptools compile --resolver backtracking --output-file=requirements/linting.txt requirements/linting.in
	python -m piptools compile --resolver backtracking --output-file=requirements/docs.txt requirements/docs.in

.PHONY: generate-dependencies-37
generate-dependencies-37:
	python -c 'import sys; sys.exit(sys.version_info[:2] != (3, 7))'
	python -m piptools compile --resolver backtracking --output-file=requirements/tests.txt requirements/tests.in
	python -m piptools compile --resolver backtracking --output-file=requirements/pyproject.txt pyproject.toml

.PHONY: format
format:
	$(isort)
	$(black)

.PHONY: lint
lint:
	flake8 --max-complexity 10 --max-line-length 120 --ignore E203,W503 dirty_equals tests
	$(isort) --check-only --df
	$(black) --check

.PHONY: test
test:
	coverage run -m pytest
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
