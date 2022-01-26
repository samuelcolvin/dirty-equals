.DEFAULT_GOAL := all
isort = poetry run isort dirty_equals tests
black = poetry run black dirty_equals tests

.PHONY: install
install:
	pip install -U pip poetry==1.2.0a2
	poetry install --with test --with lint

.PHONY: format
format:
	$(isort)
	$(black)

.PHONY: lint
lint:
	poetry run flake8 --max-complexity 10 --max-line-length 120 --ignore E203,W503 dirty_equals tests
	$(isort) --check-only --df
	$(black) --check

.PHONY: test
test:
	poetry run pytest --cov=dirty_equals

.PHONY: testcov
testcov: test
	@echo "building coverage html"
	@poetry run coverage html

.PHONY: mypy
mypy:
	poetry run mypy dirty_equals

.PHONY: all
all: lint mypy testcov

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
