# BDD Test Automation Framework

A Behavior-Driven Development (BDD) test automation framework using Python, Selenium WebDriver, and pytest-bdd. Demonstrates web browser automation, unit testing with business logic, and REST API testing, with optional Jira test result reporting.

## Features

### Test Types
- **Web Browser Tests**: Automated browser interactions with DuckDuckGo search (Chrome, Firefox, Edge)
- **Unit Tests**: Business logic testing with CucumberBasket class
- **API Tests**: REST API testing without browser automation

### Key Capabilities
- BDD approach using Gherkin syntax
- Parameterized testing with scenario outlines
- Cross-browser support
- Optional Jira integration for test reporting
- Comprehensive logging and error handling

## Setup

### Dependencies
```bash
pip install pipenv
pipenv install
pipenv shell
```

### Configuration (Optional)

#### Jira Integration
1. Copy `.env.example` to `.env`
2. Add your Jira credentials:
   ```
   JIRA_EMAIL=your-email@company.com
   JIRA_TOKEN=your-jira-api-token
   JIRA_SERVER=https://your-company.atlassian.net
   JIRA_PROJECT_KEY=YOUR_PROJECT_KEY
   ```

#### Browser Settings
Set environment variables:
- `BROWSER`: chrome, firefox, or edge (default: chrome)
- `HEADLESS`: true/false (default: true)

#### Basket Capacity
Edit `tests/basketconfig.py` to change default capacity (20 cucumbers)

## Test Scenarios

### Web Browser Tests (`tests/features/web.feature`)
```gherkin
Scenario Outline: Basic DuckDuckGo Search
  When the user searches for "<phrase>"
  Then the search results should contain "<phrase>"

Scenario Outline: Lengthy DuckDuckGo search
  When the user searches for the lengthy phrase
  Then one of the results contains "<expected_text>"
```

### Unit Tests (`tests/features/cucumbers.feature`)
```gherkin
Scenario Outline: Add cucumbers to a basket
  Given the basket has "<initial>" cucumbers
  When "<count>" cucumbers are added to the basket
  Then the basket contains "<total>" cucumbers
```

### API Tests (`tests/features/duckduckgo_api.feature`)
```gherkin
Scenario Outline: Basic DuckDuckGo API query
  Given the DuckDuckGo API is queried with "<phrase>"
  Then the response status code is "<status_code>"
```

## Running Tests

### All Tests
```bash
pipenv run python -m pytest tests/step_defs/ -v
```

### Specific Test Types
```bash
# Web browser tests
pipenv run python -m pytest tests/step_defs/test_web.py -v

# Unit tests
pipenv run python -m pytest tests/step_defs/test_cucumbers_steps.py -v

# API tests
pipenv run python -m pytest tests/step_defs/test_duckduckgo_steps.py -v
```

### Test Results
- **PASSED/FAILED**: Test status with duration
- **Jira Integration**: Automatic reporting if configured (creates issues with detailed failure info)

## Project Structure

```
BDD-course/
├── tests/
│   ├── features/           # BDD feature files
│   ├── step_defs/          # Test implementation
│   ├── browserconfig.py    # Browser settings
│   ├── basketconfig.py     # Basket capacity
│   ├── conftest.py         # Test configuration
│   └── jira_reporter.py    # Jira integration
├── cucumbers.py            # Business logic
├── Pipfile                 # Dependencies
└── README.md
```

## Contributing

Contributions are welcome! Feel free to add new test scenarios, improve browser support, or enhance reporting features.
