# BDD Test Automation Framework

A Behavior-Driven Development (BDD) test automation framework using Python, Selenium WebDriver, and pytest-bdd. This project demonstrates three different types of automated testing: web browser automation, unit testing with business logic, and REST API testing, all with automatic test result reporting to Jira.

## What This Project Does

### Three Types of Automated Testing

#### 1. Web Browser Testing
- **Web Browser Automation**: Automatically opens web browsers and performs user interactions like searching, clicking, and verifying content
- **Cross-Browser Support**: Supports Chrome, Firefox, and Safari browsers with easy configuration switching
- **DuckDuckGo Search Tests**: Includes pre-built test scenarios that search for different terms and verify results
- **Real User Interactions**: Simulates actual user behavior with mouse clicks, keyboard input, and page navigation

#### 2. Unit Testing with Business Logic
- **Cucumber Basket Tests**: Demonstrates BDD testing of business logic with a simple cucumber basket model
- **Mathematical Operations**: Tests adding and removing items with validation of business rules
- **State Management**: Verifies object state changes and boundary conditions (empty/full baskets)
- **Error Handling**: Tests proper exception handling for invalid operations
- **Configurable Capacity**: Basket maximum capacity is configurable via `basketconfig.py` (default: 20 cucumbers)

#### 3. REST API Testing
- **DuckDuckGo API Integration**: Tests REST API endpoints without browser automation
- **HTTP Response Validation**: Verifies status codes, response structure, and data integrity
- **Multiple Test Data Sets**: Includes examples for different categories (animals, fruits)
- **JSON Response Parsing**: Validates API response format and required fields

### Common Features
- **BDD Approach**: All tests are written in plain English using Gherkin syntax, making them readable by both technical and non-technical team members
- **Parameterized Testing**: Uses scenario outlines with example tables for data-driven testing
- **Comprehensive Logging**: Detailed logging for debugging and test execution tracking

### Jira Integration
- **Automatic Reporting**: Test results are automatically sent to your Jira project after each test run
- **Detailed Failure Information**: Failed tests include comprehensive error details, logs, and context to help with debugging
- **Test Execution Tracking**: Creates Jira issues to track test executions with timestamps and summaries

## How to Use

### 1. Initial Setup

#### Install Dependencies
```bash
# Install pipenv if you don't have it
pip install pipenv

# Install project dependencies
pipenv install

# Activate the virtual environment
pipenv shell
```

### 2. Configure Jira Integration (Optional)

#### Create Environment File
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your Jira credentials:
   ```
   JIRA_EMAIL=your-email@company.com
   JIRA_TOKEN=your-jira-api-token
   JIRA_SERVER=https://your-company.atlassian.net
   JIRA_PROJECT_KEY=YOUR_PROJECT_KEY
   ```

#### Getting Your Jira API Token
1. Go to your Jira account settings
2. Navigate to Security → API tokens
3. Create a new API token
4. Copy the token to your `.env` file

**Note**: If you don't configure Jira, the tests will still run normally - they just won't report results to Jira.

### 3. Configure Browser Settings

Edit `tests/browserconfig.py` to customize your browser preferences:

```python
# Choose your browser: "Chrome", "Firefox", or "Safari"
select_browser = "Chrome"

# Browser options
browser_options = Options()
# Uncomment the next line to run tests without opening browser window
# browser_options.add_argument("--headless")
```

**Browser Options**:
- **Headless Mode**: Uncomment `browser_options.add_argument("--headless")` to run tests without opening browser windows
- **Browser Choice**: Change `select_browser` to "Firefox" or "Safari" to use different browsers

### 3b. Configure Cucumber Basket Settings

Edit `tests/basketconfig.py` to customize the cucumber basket capacity:

```python
# Set the maximum capacity for cucumber baskets
basket_capacity = 20
```

**Basket Configuration Options**:
- **Capacity Limit**: Change `basket_capacity` to set the maximum number of cucumbers a basket can hold
- **Test Impact**: Modifying capacity affects validation tests that check for "basket full" conditions
- **Business Rules**: Higher capacity allows more cucumbers but may change test scenarios

### 4. Understanding Test Scenarios

The framework includes three different types of test scenarios, each demonstrating different testing approaches:

#### A. Web Browser Tests (`tests/features/web.feature`)

These tests demonstrate automated web browser interactions:

**Basic Search Tests**:
```gherkin
Scenario Outline: Basic DuckDuckGo Search
  When the user searches for "<phrase>"
  Then the search results should contain "<phrase>"

Examples:
| phrase |
| panda  |
| python |
| judge  |
```

**Long Text Search Tests**:
```gherkin
Scenario Outline: Lengthy DuckDuckGo search
  When user searches for the phrase:
  """
  When in the course of human events, it becomes necessary for one people
  to dissolve the political bands which have connected them with another...
  """
  Then one of the results contains "<expected_text>"

Examples:
| expected_text |
| people        |
| human events  |
```

#### B. Unit/Business Logic Tests (`tests/features/cucumbers.feature`)

These tests demonstrate BDD testing of business logic without external dependencies:

**Adding Cucumbers**:
```gherkin
Scenario Outline: Add cucumbers to a basket
  Given the basket has "<initial>" cucumbers
  When "<count>" cucumbers are added to the basket
  Then the basket contains "<total>" cucumbers

Examples: Amounts of cucumbers
| initial | count | total |
| 2       | 4     | 6     |
| 3       | 5     | 8     |
| 0       | 7     | 7     |
```

**Removing Cucumbers**:
```gherkin
Scenario: Remove cucumbers from a basket
  Given the basket has "8" cucumbers
  When "3" cucumbers are removed from the basket
  Then the basket contains "5" cucumbers
```

#### C. REST API Tests (`tests/features/duckduckgo_api.feature`)

These tests demonstrate API testing without browser automation:

**API Response Validation**:
```gherkin
Scenario Outline: Basic DuckDuckGo API query
  Given the DuckDuckGo API is queried with "<phrase>"
  Then the response status code is "<status_code>"
  And the response contains results for "<phrase>"
  And the phrase "<phrase>" appears somewhere in the response

Examples: Animals
| phrase | status_code |
| cat    | 202         |
| dog    | 202         |
| panda  | 202         |

Examples: Fruits
| phrase | status_code |
| apple  | 202         |
| orange | 202         |
| banana | 202         |
```

#### Customizing Test Data

You can modify any of the test scenarios by editing the Examples tables:

**Web Tests**: 
- Add new search terms to test different queries
- Modify expected results for verification

**Cucumber Tests**: 
- Change initial counts, add/remove amounts, and expected totals
- Add new scenarios for edge cases (full basket, empty basket)
- Modify `basket_capacity` in `tests/basketconfig.py` to test different capacity limits
- Create scenarios that test capacity validation (e.g., trying to add too many cucumbers)

**API Tests**: 
- Add new search phrases and categories
- Test different API parameters and response validation

### 5. Running Tests

#### Option 1: Run Tests in GitHub Actions

You can run tests directly in GitHub Actions:

1. Go to the "Actions" tab in your GitHub repository
2. Select "Run BDD Tests" from the left sidebar
3. Click the "Run workflow" button
4. Click the green "Run workflow" button in the popup

This will run all tests in a fresh GitHub-hosted environment and show you the results.

#### Option 2: Run All Tests Locally (All Types)
```bash
# Run all test types together
pipenv run python -m pytest tests/step_defs/ -v

# Run all tests in parallel for faster execution
pipenv run python -m pytest tests/step_defs/ -v -n auto
```

#### Run Specific Test Types

**Web Browser Tests**:
```bash
# Run all web tests
pipenv run python -m pytest tests/step_defs/test_web.py -v

# Run only basic search tests
pipenv run python -m pytest tests/step_defs/test_web.py::test_basic_duckduckgo_search -v

# Run only lengthy search tests
pipenv run python -m pytest tests/step_defs/test_web.py::test_lengthy_duckduckgo_search -v
```

**Cucumber Basket Tests**:
```bash
# Run all cucumber basket tests
pipenv run python -m pytest tests/step_defs/test_cucumbers_steps.py -v

# Run specific cucumber scenarios
pipenv run python -m pytest tests/step_defs/test_cucumbers_steps.py::test_add_cucumbers_to_a_basket -v
pipenv run python -m pytest tests/step_defs/test_cucumbers_steps.py::test_remove_cucumbers_from_a_basket -v
```

**DuckDuckGo API Tests**:
```bash
# Run all API tests
pipenv run python -m pytest tests/step_defs/test_duckduckgo_steps.py -v

# Run specific API test scenarios
pipenv run python -m pytest tests/step_defs/test_duckduckgo_steps.py::test_basic_duckduckgo_api_query -v
```

#### Run Tests by Feature File
```bash
# Run tests for specific feature files
pipenv run python -m pytest --gherkin-terminal-reporter -v tests/step_defs/test_web.py
pipenv run python -m pytest --gherkin-terminal-reporter -v tests/step_defs/test_cucumbers_steps.py
pipenv run python -m pytest --gherkin-terminal-reporter -v tests/step_defs/test_duckduckgo_steps.py
```

### 6. Understanding Test Results

#### Console Output
- **PASSED**: Test completed successfully
- **FAILED**: Test encountered an error (details will be shown)
- **Duration**: How long each test took to run

#### Jira Reports (if configured)
- A new Jira issue is created for each test run
- Failed tests include detailed error information and logs
- Test execution summaries show overall results

## Project Structure

```
BDD-course/
├── tests/
│   ├── features/                # BDD feature files (test scenarios in plain English)
│   │   ├── web.feature          # Web browser automation tests
│   │   ├── cucumbers.feature    # Unit/business logic tests
│   │   └── duckduckgo_api.feature # REST API tests
│   ├── step_defs/               # Test implementation code
│   │   ├── __init__.py
│   │   ├── test_web.py          # Web browser test steps
│   │   ├── test_cucumbers_steps.py # Cucumber basket test steps
│   │   └── test_duckduckgo_steps.py # API test steps
│   ├── __init__.py
│   ├── basketconfig.py          # Cucumber basket configuration (capacity settings)
│   ├── browserconfig.py         # Browser configuration for web tests
│   ├── conftest.py             # Test configuration and fixtures
│   └── jira_reporter.py        # Jira integration for test reporting
├── cucumbers.py                # CucumberBasket class (business logic)
├── .env.example                # Example environment configuration
├── .env                        # Your actual environment variables (not in git)
├── .gitignore                  # Git ignore rules
├── Pipfile                     # Python dependencies
├── Pipfile.lock               # Locked dependency versions
├── LICENSE                     # MIT License
└── README.md                   # This file
```

### Test Types Overview

| Test Type | Feature File | Step Definition | Purpose |
|-----------|-------------|----------------|---------|
| **Web Browser** | `web.feature` | `test_web.py` | Automated browser interactions with DuckDuckGo search |
| **Unit/Business Logic** | `cucumbers.feature` | `test_cucumbers_steps.py` | Testing business logic with CucumberBasket class |
| **REST API** | `duckduckgo_api.feature` | `test_duckduckgo_steps.py` | API testing without browser automation |

## Troubleshooting

### Common Issues

1. **Browser not found**: Make sure you have Chrome, Firefox, or Safari installed
2. **Jira connection failed**: Check your `.env` file credentials and network connection
3. **Tests running slowly**: Enable headless mode in `browserconfig.py` for faster execution
4. **Import errors**: Make sure you're running tests with `pipenv run` to use the correct environment

### Getting Help

- Check the console output for detailed error messages
- Review the Jira issue comments for test failure details
- Ensure all dependencies are installed with `pipenv install`

## Credits

This project was inspired by and built upon the excellent educational resources created by **Andrew Knight** ([@AutomationPanda](https://github.com/AutomationPanda)):

### 📚 **Learning Resources**
- **[Behavior-Driven Python with pytest-bdd](https://testautomationu.applitools.com/behavior-driven-python-with-pytest-bdd/)** - A comprehensive course on Test Automation University that teaches BDD fundamentals with Python and pytest-bdd
- **[behavior-driven-python Repository](https://github.com/AutomationPanda/behavior-driven-python)** - The companion repository containing examples and code from the course

### 🙏 **Acknowledgments**
Special thanks to Andrew Knight for creating outstanding educational content that makes BDD and test automation accessible to developers and testers. His clear explanations and practical examples provided the foundation for understanding pytest-bdd and implementing this framework.

## Contributing

Feel free to add new test scenarios by:
1. Adding new examples to the feature files
2. Creating new feature files for different websites or functionality
3. Extending the browser configuration options
4. Improving the Jira reporting features
