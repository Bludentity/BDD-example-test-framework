---
description: Repository Information Overview
alwaysApply: true
---

# BDD Test Automation Framework Information

## Summary
A Behavior-Driven Development (BDD) test automation framework using Python, Selenium WebDriver, and pytest-bdd. The project demonstrates three types of automated testing: web browser automation, unit testing with business logic, and REST API testing, with optional Jira test result reporting.

## Structure
- **tests/**: Contains all test-related files including features, step definitions, and configuration
  - **features/**: BDD feature files written in Gherkin syntax
  - **step_defs/**: Python implementation of test steps
- **cucumbers.py**: Business logic class for cucumber basket tests
- **.github/workflows/**: CI/CD configuration for GitHub Actions

## Language & Runtime
**Language**: Python
**Version**: 3.10.18
**Build System**: pip/pipenv
**Package Manager**: pipenv

## Dependencies
**Main Dependencies**:
- pytest (7.4.4): Testing framework
- pytest-bdd (6.1.1): BDD plugin for pytest
- selenium (4.18.1): Web browser automation
- requests (2.31.0): HTTP client for API testing
- python-dotenv (1.0.1): Environment variable management
- webdriver-manager (4.0.1): WebDriver management
- pytest-xdist (3.5.0): Parallel test execution

## Build & Installation
```bash
# Install dependencies
pip install pipenv
pipenv install

# Activate virtual environment
pipenv shell

# Run all tests
python -m pytest tests/step_defs/ -v

# Run specific test types
python -m pytest tests/step_defs/test_web.py -v
python -m pytest tests/step_defs/test_cucumbers_steps.py -v
python -m pytest tests/step_defs/test_duckduckgo_steps.py -v
```

## Testing
**Framework**: pytest with pytest-bdd
**Test Location**: 
- Feature files: `tests/features/`
- Step definitions: `tests/step_defs/`

**Test Types**:
1. **Web Browser Tests**: Automated browser interactions with DuckDuckGo search
   - Feature file: `web.feature`
   - Step definition: `test_web.py`

2. **Unit/Business Logic Tests**: Testing business logic with CucumberBasket class
   - Feature file: `cucumbers.feature`
   - Step definition: `test_cucumbers_steps.py`
   - Business logic: `cucumbers.py`

3. **REST API Tests**: API testing without browser automation
   - Feature file: `duckduckgo_api.feature`
   - Step definition: `test_duckduckgo_steps.py`

**Configuration**:
- **Browser Configuration**: `tests/browserconfig.py`
  - Supports Chrome, Firefox, and Edge
  - Configurable via environment variables (BROWSER, HEADLESS)
- **Cucumber Basket Configuration**: `tests/basketconfig.py`
  - Default capacity: 20 cucumbers

**CI/CD Integration**:
- GitHub Actions workflow in `.github/workflows/test.yml`
- Runs tests in headless Chrome browser on Ubuntu

**Jira Integration**:
- Optional test result reporting to Jira
- Configured via environment variables in `.env` file
- Implementation in `tests/jira_reporter.py`