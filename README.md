# BDD Test Automation Framework

A Behavior-Driven Development (BDD) test automation framework using Python, Selenium WebDriver, and pytest-bdd. This project demonstrates automated web testing with DuckDuckGo search functionality and includes automatic test result reporting to Jira.

## What This Project Does

### Automated Web Testing
- **Web Browser Automation**: Automatically opens web browsers and performs user interactions like searching, clicking, and verifying content
- **Cross-Browser Support**: Supports Chrome, Firefox, and Safari browsers with easy configuration switching
- **DuckDuckGo Search Tests**: Includes pre-built test scenarios that search for different terms and verify results
- **BDD Approach**: Tests are written in plain English using Gherkin syntax, making them readable by both technical and non-technical team members

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

### 4. Understanding Test Scenarios

The tests are defined in `tests/features/web.feature` using simple English:

#### Basic Search Tests
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

#### Customizing Test Data
You can modify the test data by editing the Examples table:
- **Add new search terms**: Add more rows to the `| phrase |` column
- **Change search terms**: Replace existing terms with your preferred search queries

#### Long Text Search Tests
```gherkin
Scenario Outline: Lengthy DuckDuckGo search
  When user searches for the phrase:
  """
  Your long search text here...
  """
  Then one of the results contains "<expected_text>"
```

### 5. Running Tests

#### Run All Tests
```bash
pipenv run python -m pytest tests/step_defs/test_web.py -v
```

#### Run Specific Test Scenarios
```bash
# Run only basic search tests
pipenv run python -m pytest tests/step_defs/test_web.py::test_basic_duckduckgo_search -v

# Run only lengthy search tests
pipenv run python -m pytest tests/step_defs/test_web.py::test_lengthy_duckduckgo_search -v
```

#### Run Tests in Parallel (Faster)
```bash
pipenv run python -m pytest tests/step_defs/test_web.py -v -n auto
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
│   ├── features/
│   │   └── web.feature          # Test scenarios in plain English
│   ├── step_defs/
│   │   └── test_web.py          # Test implementation code
│   ├── browserconfig.py         # Browser configuration
│   ├── conftest.py             # Test configuration and fixtures
│   └── jira_reporter.py        # Jira integration
├── .env.example                # Example environment configuration
├── .gitignore                  # Git ignore rules
├── Pipfile                     # Python dependencies
└── README.md                   # This file
```

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
