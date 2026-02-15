.PHONY: help install install-dev test test-cov clean lint format run-examples

help:
	@echo "AI Personal Assistant - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install        Install the package"
	@echo "  make install-dev    Install in development mode"
	@echo "  make test           Run tests"
	@echo "  make test-cov       Run tests with coverage report"
	@echo "  make clean          Clean up generated files"
	@echo "  make lint           Run linting (if configured)"
	@echo "  make format         Format code (if configured)"
	@echo "  make run-examples   Run example script"

install:
	pip install .

install-dev:
	pip install -e .
	pip install pytest pytest-cov pytest-mock

test:
	pytest

test-cov:
	pytest --cov=ai_assistant --cov-report=html --cov-report=term

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

lint:
	@echo "Run your preferred linter here (e.g., pylint, flake8)"
	@echo "Example: pylint ai_assistant/"

format:
	@echo "Run your preferred formatter here (e.g., black, autopep8)"
	@echo "Example: black ai_assistant/ tests/"

run-examples:
	python examples.py
