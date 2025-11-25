import os
import tempfile
import shutil
import logging
import pytest
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from tests.browserconfig import browser_options, select_browser


SCREENSHOT_DIR = tempfile.mkdtemp(prefix="bdd_screenshots_")


def ensure_default_environment():
    env_path = Path(__file__).parent.parent / '.env'
    default_env = {
        'HEADLESS': 'true',
        'BROWSER': 'chrome'
    }

    load_dotenv(dotenv_path=env_path, override=False)

    for key, value in default_env.items():
        if not os.getenv(key):
            os.environ[key] = value


ensure_default_environment()


@pytest.fixture(scope="function")
def browser(request):
    temp_dir = tempfile.mkdtemp()
    driver = None

    try:
        browser_name = select_browser()
        options = browser_options(browser_name)

        if browser_name.lower() != 'firefox':
            options.add_argument(f"--user-data-dir={temp_dir}")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")

        if browser_name.lower() == 'chrome':
            driver = webdriver.Chrome(options=options)
            browser_info = 'Chrome'
        elif browser_name.lower() == 'firefox':
            driver = webdriver.Firefox(options=options)
            browser_info = 'Firefox'
        elif browser_name.lower() == 'edge':
            driver = webdriver.Edge(options=options)
            browser_info = 'Edge'
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")

        if hasattr(request.node, 'user_properties'):
            request.node.user_properties.append(('browser', browser_info))

        driver.implicitly_wait(10)
        driver.maximize_window()

        yield driver
        driver.quit()
    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as error:
            logging.warning(f"Failed to clean up temporary directory {temp_dir}: {error}")


JIRA_ENABLED = all([
    os.getenv('JIRA_EMAIL'),
    os.getenv('JIRA_TOKEN'),
    os.getenv('JIRA_PROJECT_KEY')
])


if JIRA_ENABLED:
    from .jira_reporter import JiraReporter, report_test_results


def pytest_configure(config):
    config.option.markers = "jira: Mark tests that should be reported to Jira"
    config.option.junit_family = "xunit2"

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if not hasattr(item, 'rep_call'):
        item.rep_call = rep

    if rep.when == 'call' and rep.failed:
        pass


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    global SCREENSHOT_DIR

    if not JIRA_ENABLED:
        terminalreporter.write_line("\nJira reporting is disabled. Set JIRA_EMAIL, JIRA_TOKEN, and JIRA_PROJECT_KEY in .env to enable.")
        return

    test_results = []

    try:
        browser_name = select_browser().title()
        browser_info = f"{browser_name}"
        print(f"Using browser: {browser_info}")
    except Exception as error:
        print(f"Error getting browser info: {str(error)}")
        browser_info = "Unknown"
    
    for test in terminalreporter.stats.get('passed', []):
        duration = getattr(test, 'duration', 0)
        test_results.append({
            'name': test.nodeid.split('::')[-1],
            'status': 'PASS',
            'comment': f'Test passed in {duration:.2f}s',
            'full_name': test.nodeid,
            'duration': duration,
            'metadata': {
                'browser': browser_info or 'Unknown',
                'node_id': test.nodeid
            }
        })
    
    for test in terminalreporter.stats.get('failed', []):
        failure_info = _extract_failure_details(test)
        duration = getattr(test, 'duration', 0)
        
        test_results.append({
            'name': test.nodeid.split('::')[-1],
            'status': 'FAIL',
            'comment': f'Test failed in {duration:.2f}s',
            'full_name': test.nodeid,
            'duration': duration,
            'failure_details': failure_info,
            'logs': _capture_test_logs(test),
            'stdout': getattr(test, 'capstdout', ''),
            'stderr': getattr(test, 'capstderr', ''),
            'metadata': {
                'browser': browser_info or 'Unknown',
                'node_id': test.nodeid,
                'outcome': 'failed'
            }
        })
    
    for test in terminalreporter.stats.get('error', []):
        error_info = _extract_failure_details(test)
        duration = getattr(test, 'duration', 0)
        
        test_results.append({
            'name': test.nodeid.split('::')[-1],
            'status': 'ERROR',
            'comment': f'Test error in {duration:.2f}s',
            'full_name': test.nodeid,
            'duration': duration,
            'failure_details': error_info,
            'logs': _capture_test_logs(test),
            'stdout': getattr(test, 'capstdout', ''),
            'stderr': getattr(test, 'capstderr', ''),
            'metadata': {
                'browser': browser_info or 'Unknown',
                'node_id': test.nodeid,
                'outcome': 'error'
            }
        })
    
    if test_results:
        try:
            result = report_test_results(test_results, browser_info=browser_info)
            if result:
                terminalreporter.write_line("\nSuccessfully reported test results to Jira")

                issue_key = result.get('key')
                if issue_key:
                    from tests.jira_reporter import JiraReporter
                    reporter = JiraReporter()
                    import os
                    print(f"Looking for screenshots in: {SCREENSHOT_DIR}")
                    if os.path.exists(SCREENSHOT_DIR):
                        screenshot_files = [f for f in os.listdir(SCREENSHOT_DIR) if f.endswith('.png')]
                        print(f"Found {len(screenshot_files)} screenshot files: {screenshot_files}")
                        for filename in screenshot_files:
                            screenshot_path = os.path.join(SCREENSHOT_DIR, filename)
                            print(f"Attaching screenshot: {screenshot_path}")
                            success = reporter.attach_file(issue_key, screenshot_path, filename)
                            if success:
                                try:
                                    os.remove(screenshot_path)
                                    print(f"Removed screenshot after attachment: {filename}")
                                except Exception as error:
                                    print(f"Failed to remove screenshot {filename}: {error}")
                            else:
                                print(f"Failed to attach screenshot: {filename}")
                    else:
                        print(f"Screenshot directory does not exist: {SCREENSHOT_DIR}")

            else:
                terminalreporter.write_line("\nFailed to report results to Jira")
        except Exception as error:
            terminalreporter.write_line(f"\nError reporting to Jira: {str(error)}", red=True)
    else:
        terminalreporter.write_line("\nNo test results to report to Jira")

    try:
        shutil.rmtree(SCREENSHOT_DIR, ignore_errors=True)
    except Exception as error:
        print(f"Failed to clean up screenshot directory {SCREENSHOT_DIR}: {error}")


def _extract_failure_details(test_report):
    failure_info = {
        'short_summary': '',
        'long_summary': '',
        'traceback': '',
        'assertion_error': ''
    }
    
    if hasattr(test_report, 'longrepr') and test_report.longrepr:
        failure_info['long_summary'] = str(test_report.longrepr)
        
        if hasattr(test_report.longrepr, 'reprcrash'):
            failure_info['short_summary'] = str(test_report.longrepr.reprcrash)
        
        if hasattr(test_report.longrepr, 'reprtraceback'):
            failure_info['traceback'] = str(test_report.longrepr.reprtraceback)
        
        longrepr_str = str(test_report.longrepr)
        if 'AssertionError' in longrepr_str:
            lines = longrepr_str.split('\n')
            for index, line in enumerate(lines):
                if 'AssertionError' in line:
                    start = max(0, index-2)
                    end = min(len(lines), index+3)
                    failure_info['assertion_error'] = '\n'.join(lines[start:end])
                    break
    
    return failure_info


def _capture_test_logs(test_report):
    logs = {
        'captured_logs': '',
        'captured_stdout': '',
        'captured_stderr': ''
    }
    
    if hasattr(test_report, 'caplog') and test_report.caplog:
        logs['captured_logs'] = test_report.caplog
    
    if hasattr(test_report, 'capstdout') and test_report.capstdout:
        logs['captured_stdout'] = test_report.capstdout
    
    if hasattr(test_report, 'capstderr') and test_report.capstderr:
        logs['captured_stderr'] = test_report.capstderr
    
    if hasattr(test_report, 'sections'):
        for section_name, section_content in test_report.sections:
            if 'log' in section_name.lower():
                logs[f'section_{section_name}'] = section_content
            elif 'stdout' in section_name.lower():
                logs['captured_stdout'] = section_content
            elif 'stderr' in section_name.lower():
                logs['captured_stderr'] = section_content
    
    return logs