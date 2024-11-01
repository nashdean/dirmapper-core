# Define the paths
PYPROJECT_TOML = pyproject.toml
SRC_DIR = dirmapper_core

# Extract the version from pyproject.toml
VERSION := $(shell grep '^version' pyproject.toml | head -n 1 | sed -E 's/version = "(.*)"/\1/')

# Define the package name
PACKAGE_NAME = dirmapper_core

.PHONY: build clean install uninstall reinstall check-pytest-cov run-coverage


build: clean
	@echo "Building the package..."
	python -m build

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build dist $(SRC_DIR)/*.egg-info

install: build
	@echo "Installing the package..."
	pip install dist/$(PACKAGE_NAME)-$(VERSION)-py3-none-any.whl

uninstall:
	@echo "Uninstalling the package..."
	yes | pip uninstall $(PACKAGE_NAME)

reinstall: uninstall install
	@echo "Reinstalling the package..."

# Check if pytest-cov is installed
check-pytest-cov:
	@python3 -m pip show pytest-cov > /dev/null || (echo "pytest-cov is not installed. Please install it using 'pip install pytest-cov'." && exit 1)

# Run the coverage command
run-coverage: check-pytest-cov
	@echo "Running coverage tests..."
	@python3 -m pytest --cov=dirmapper tests/

# Run the coverage command
run-coverage-html: check-pytest-cov
	@echo "Running coverage tests..."
	@python3 -m pytest --cov=dirmapper --cov-report=html

# Add a default command to run coverage in html
coverage-vv: run-coverage-html

# Add a default command to run coverage
cov: run-coverage
coverage: cov
