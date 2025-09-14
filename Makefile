.PHONY: setup check test test-cov clean format lint

PYTHON := python3.11
VENV := venv
ACTIVATE := $(VENV)/bin/activate

setup:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -e .

check: lint test

test:
	$(ACTIVATE) && python3.11 -m pytest tests/ -v

test-cov:
	$(ACTIVATE) && python3.11 -m pytest tests/ --cov=src/automata --cov-report=html --cov-report=term-missing

clean:
	rm -rf $(VENV)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

format:
	$(ACTIVATE) && black src/ tests/ --line-length 100

lint:
	$(ACTIVATE) && flake8 src/ tests/ --ignore=E203,W503,E722
