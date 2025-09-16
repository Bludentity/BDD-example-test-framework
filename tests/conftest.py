"""
Pytest configuration and Jira reporting.
"""
import os
import tempfile
import shutil
import pytest
import logging
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from tests.browserconfig import browser_options, select_browser


@pytest.fixture
def browser():
    """Set up and tear down the browser for web tests."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        if select_browser == "Chrome":
            # Create a copy of the options to avoid modifying the global one
            chrome_options = browser_options
            chrome_options.add_argument(f"--user-data-dir={temp_dir}")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            driver = webdriver.Chrome(options=chrome_options)
        elif select_browser == "Firefox":
            driver = webdriver.Firefox(options=browser_options)
        elif select_browser == "Safari":
            driver = webdriver.Safari(options=browser_options)
        else:
            raise ValueError(f"Unsupported browser: {select_browser}")

        driver.implicitly_wait(10)
        driver.maximize_window()

        yield driver
        driver.quit()
    finally:
        # Clean up the temporary directory
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logging.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")


# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import JiraReporter only if credentials are available
JIRA_ENABLED = all([
    os.getenv('JIRA_EMAIL'),
    os.getenv('JIRA_TOKEN'),
    os.getenv('JIRA_PROJECT_KEY')
])

if JIRA_ENABLED:
    from .jira_reporter import JiraReporter, report_test_results

def pytest_configure(config):
    """Configure test settings."""
    config.option.markers = "jira: Mark tests that should be reported to Jira"
    config.option.junit_family = "xunit2"
    
    # Configure logging to capture more details
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Report test results to Jira after test run completes."""
    if not JIRA_ENABLED:
        terminalreporter.write_line("\nJira reporting is disabled. Set JIRA_EMAIL, JIRA_TOKEN, and JIRA_PROJECT_KEY in .env to enable.")
        return
    
    # Collect test results
    test_results = []
    
    # Add passed tests
    for test in terminalreporter.stats.get('passed', []):
        test_results.append({
            'name': test.nodeid.split('::')[-1],
            'status': 'PASS',
            'comment': f'Test passed in {test.duration:.2f}s',
            'full_name': test.nodeid,
            'duration': test.duration
        })
    
    # Add failed tests with detailed information
    for test in terminalreporter.stats.get('failed', []):
        # Extract detailed failure information
        failure_info = _extract_failure_details(test)
        
        test_results.append({
            'name': test.nodeid.split('::')[-1],
            'status': 'FAIL',
            'comment': f'Test failed in {test.duration:.2f}s',
            'full_name': test.nodeid,
            'duration': test.duration,
            'failure_details': failure_info,
            'logs': _capture_test_logs(test),
            'stdout': getattr(test, 'capstdout', ''),
            'stderr': getattr(test, 'capstderr', '')
        })
    
    # Add error tests with detailed information
    for test in terminalreporter.stats.get('error', []):
        # Extract detailed error information
        error_info = _extract_failure_details(test)
        
        test_results.append({
            'name': test.nodeid.split('::')[-1],
            'status': 'FAIL',
            'comment': f'Test error in {test.duration:.2f}s',
            'full_name': test.nodeid,
            'duration': test.duration,
            'failure_details': error_info,
            'logs': _capture_test_logs(test),
            'stdout': getattr(test, 'capstdout', ''),
            'stderr': getattr(test, 'capstderr', '')
        })
    
    # Report to Jira
    if test_results:
        try:
            result = report_test_results(test_results)
            if result:
                terminalreporter.write_line("\nSuccessfully reported test results to Jira")
            else:
                terminalreporter.write_line("\nFailed to report results to Jira")
        except Exception as e:
            terminalreporter.write_line(f"\nError reporting to Jira: {str(e)}", red=True)
    else:
        terminalreporter.write_line("\nNo test results to report to Jira")


def _extract_failure_details(test_report):
    """Extract detailed failure information from a test report."""
    failure_info = {
        'short_summary': '',
        'long_summary': '',
        'traceback': '',
        'assertion_error': ''
    }
    
    if hasattr(test_report, 'longrepr') and test_report.longrepr:
        # Get the full failure representation
        failure_info['long_summary'] = str(test_report.longrepr)
        
        # Try to extract specific parts
        if hasattr(test_report.longrepr, 'reprcrash'):
            failure_info['short_summary'] = str(test_report.longrepr.reprcrash)
        
        # Extract traceback if available
        if hasattr(test_report.longrepr, 'reprtraceback'):
            failure_info['traceback'] = str(test_report.longrepr.reprtraceback)
        
        # Look for assertion errors
        longrepr_str = str(test_report.longrepr)
        if 'AssertionError' in longrepr_str:
            lines = longrepr_str.split('\n')
            for i, line in enumerate(lines):
                if 'AssertionError' in line:
                    # Get the assertion error and a few lines of context
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    failure_info['assertion_error'] = '\n'.join(lines[start:end])
                    break
    
    return failure_info


def _capture_test_logs(test_report):
    """Capture logs from a test execution."""
    logs = {
        'captured_logs': '',
        'captured_stdout': '',
        'captured_stderr': ''
    }
    
    # Try to get captured logs from different sources
    if hasattr(test_report, 'caplog') and test_report.caplog:
        logs['captured_logs'] = test_report.caplog
    
    if hasattr(test_report, 'capstdout') and test_report.capstdout:
        logs['captured_stdout'] = test_report.capstdout
    
    if hasattr(test_report, 'capstderr') and test_report.capstderr:
        logs['captured_stderr'] = test_report.capstderr
    
    # Try to get sections if available
    if hasattr(test_report, 'sections'):
        for section_name, section_content in test_report.sections:
            if 'log' in section_name.lower():
                logs[f'section_{section_name}'] = section_content
            elif 'stdout' in section_name.lower():
                logs['captured_stdout'] = section_content
            elif 'stderr' in section_name.lower():
                logs['captured_stderr'] = section_content
    
    return logs