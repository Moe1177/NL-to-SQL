.ONESHELL:
SHELL=/bin/bash
PYTHON_VERSION=3.11.8

# Colors for output
GREEN=\033[0;32m
YELLOW=\033[1;33m
CYAN=\033[0;36m
RED=\033[0;31m
NC=\033[0m # No Color

.PHONY: help datalink env update-lock update-env clean

# Default target - show help
help:
	@echo -e "$(CYAN)FastAPI Backend Build Script$(NC)"
	@echo -e "$(YELLOW)Available commands:$(NC)"
	@echo "  datalink [PATH] [SHORTCUT] - Create a symbolic link"
	@echo "  env                        - Set up Python environment"
	@echo "  update-lock                - Update lock file"
	@echo "  update-env                 - Update environment packages"
	@echo "  clean                      - Clean project files"

datalink:
	@if [ -z "$(PATH_ARG)" ] || [ -z "$(SHORTCUT_ARG)" ]; then \
		echo -e "$(RED)Usage: make datalink PATH_ARG=<path> SHORTCUT_ARG=<shortcut>$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(YELLOW)Creating symbolic link...$(NC)"
	@ln -sf $(PATH_ARG) $(SHORTCUT_ARG)
	@echo -e "$(GREEN)Symbolic link created!$(NC)"

env:
	@echo -e "$(GREEN)Setting up Python environment...$(NC)"
	
	# Check if Python is available
	@if ! command -v python3 &> /dev/null; then \
		echo -e "$(RED)Python not found. Please install Python $(PYTHON_VERSION)$(NC)"; \
		exit 1; \
	fi
	
	# Check if Poetry is installed, install if not
	@if ! command -v poetry &> /dev/null; then \
		echo -e "$(YELLOW)Installing Poetry...$(NC)"; \
		python3 -m pip install --upgrade pip; \
		pip install poetry==1.8.5; \
	fi
	
	# Configure Poetry to create virtual environment in project directory
	@echo -e "$(YELLOW)Configuring Poetry...$(NC)"
	@poetry config virtualenvs.in-project true
	
	# Install dependencies using Poetry
	@echo -e "$(YELLOW)Installing dependencies with Poetry...$(NC)"
	@poetry install --with dev
	
	@echo -e "$(GREEN)Environment setup complete!$(NC)"
	@echo -e "$(CYAN)To activate the environment, run: poetry shell$(NC)"

update-lock:
	@echo -e "$(YELLOW)Updating lock file...$(NC)"
	@poetry lock
	@echo -e "$(GREEN)Lock file updated!$(NC)"

update-env:
	@echo -e "$(YELLOW)Updating environment...$(NC)"
	@poetry install --no-root --all-extras --with dev,test,code-quality,notebook
	@echo -e "$(GREEN)Environment updated!$(NC)"

clean:
	@echo -e "$(YELLOW)Cleaning project files...$(NC)"
	
	# Remove pycache files
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	
	# Remove egg-info directories
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	
	# Remove coverage files
	@rm -f .coverage 2>/dev/null || true
	
	@echo -e "$(GREEN)Project cleaned!$(NC)"

# Legacy targets (for backward compatibility)
install: env

# Add a development server target
dev:
	@echo -e "$(GREEN)Starting development server...$(NC)"
	@poetry run python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Add a test target
test:
	@echo -e "$(GREEN)Running tests...$(NC)"
	@poetry run pytest

# Add a lint target
lint:
	@echo -e "$(GREEN)Running linters...$(NC)"
	@poetry run ruff check .
	@poetry run black --check .

# Add a format target
format:
	@echo -e "$(GREEN)Formatting code...$(NC)"
	@poetry run black .
	@poetry run ruff --fix .
