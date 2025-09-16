"""
Jira test reporting module.
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class JiraReporter:
    """Handles reporting test results to Jira."""
    
    def __init__(self):
        self.server = os.getenv('JIRA_SERVER')
        self.email = os.getenv('JIRA_EMAIL')
        self.token = os.getenv('JIRA_TOKEN')
        self.project_key = os.getenv('JIRA_PROJECT_KEY')
        self.test_plan_key = os.getenv('JIRA_TEST_PLAN_KEY')
        self.verify_credentials()
    
    def verify_credentials(self):
        """Verify that all required credentials are present."""
        if not all([self.server, self.email, self.token, self.project_key]):
            raise ValueError(
                "Jira credentials not properly configured. "
                "Please set JIRA_EMAIL, JIRA_TOKEN, and JIRA_PROJECT_KEY in .env file"
            )
    
    def create_test_execution(self, test_results):
        """Create a test execution issue in Jira using standard REST API."""
        # Create a summary of test results
        passed = sum(1 for test in test_results if test['status'] == 'PASS')
        failed = sum(1 for test in test_results if test['status'] == 'FAIL')
        total = len(test_results)
        
        # Create an issue to track the test execution
        issue_data = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": f"Test Execution - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "description": self._format_test_results_description(test_results, passed, failed, total),
                "issuetype": {
                    "name": "Task"  # You can change this to another issue type that better suits you
                },
                "labels": ["automated-test", "bdd-test"] # You can edit or add more labels if needed
            }
        }
        
        # Send request to create issue
        try:
            url = f"{self.server}/rest/api/2/issue"
            response = requests.post(
                url,
                json=issue_data,
                auth=(self.email, self.token),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            result = response.json()
            
            # Add a comment with detailed test results
            self._add_test_results_comment(result['key'], test_results)
            
            return result
        except Exception as e:
            print(f"Failed to report to Jira: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def _format_test_results_description(self, test_results, passed, failed, total):
        """Format test results into a description."""
        status_emoji = "✅" if failed == 0 else "❌"
        description = f"{status_emoji} **Test Execution Summary**\n\n"
        description += f"* Total Tests: {total}\n"
        description += f"* Passed: {passed}\n"
        description += f"* Failed: {failed}\n"
        description += f"* Success Rate: {(passed/total*100):.1f}%\n\n"
        
        if failed > 0:
            description += "**Failed Tests:**\n"
            for test in test_results:
                if test['status'] == 'FAIL':
                    description += f"* {test['name']}\n"
        
        return description
    
    def _add_test_results_comment(self, issue_key, test_results):
        """Add detailed test results as a comment."""
        try:
            comment_body = "*Detailed Test Results:*\n\n"
            
            for test in test_results:
                status_symbol = "(/) " if test['status'] == 'PASS' else "(x) "
                # Sanitize test name to avoid special characters
                test_name = self._sanitize_text(test['name'])
                comment_body += f"{status_symbol}*{test_name}* - {test['status']}\n"
                
                if test.get('comment'):
                    comment_body += f"Duration: {test.get('duration', 0):.2f}s\n"
                
                # Add detailed failure information for failed tests
                if test['status'] == 'FAIL' and test.get('failure_details'):
                    failure_details = self._format_failure_details(test)
                    # Limit the size of failure details to avoid API limits
                    if len(failure_details) > 2000:
                        failure_details = failure_details[:2000] + "\n\n... (truncated due to length)"
                    comment_body += failure_details
                
                comment_body += "\n"
            
            # Ensure comment body is not too long (Jira has limits)
            if len(comment_body) > 32000:
                comment_body = comment_body[:32000] + "\n\n... (truncated due to length)"
            
            comment_data = {
                "body": comment_body
            }
            
            url = f"{self.server}/rest/api/2/issue/{issue_key}/comment"
            response = requests.post(
                url,
                json=comment_data,
                auth=(self.email, self.token),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            print(f"Successfully added detailed comment to Jira issue {issue_key}")
        except requests.exceptions.HTTPError as e:
            print(f"Failed to add comment to Jira issue: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
        except Exception as e:
            print(f"Failed to add comment to Jira issue: {str(e)}")
    
    def _format_failure_details(self, test):
        """Format detailed failure information for a failed test, prioritizing logger comments."""
        failure_details = test.get('failure_details', {})
        logs = test.get('logs', {})
        
        details = "\n*Failure Details:*\n"
        
        # Priority 1: Logger comments (most important - describes where failure occurred)
        logger_comments = self._extract_logger_comments(logs, failure_details)
        if logger_comments:
            details += "*Where the failure occurred:*\n"
            details += f"{logger_comments}\n\n"
        
        # Priority 2: Specific error information (assertion errors, exceptions)
        error_info = self._extract_specific_error(failure_details)
        if error_info:
            details += "*Specific Error:*\n"
            details += "{code:title=Error Details}\n"
            details += error_info
            details += "\n{code}\n\n"
        
        # Priority 3: Only add verbose logs if logger comments are not available or very short
        if not logger_comments or len(logger_comments) < 100:
            verbose_logs = self._extract_verbose_logs(logs)
            if verbose_logs:
                details += "*Additional Context:*\n"
                details += verbose_logs
        
        return details
    
    def _extract_logger_comments(self, logs, failure_details):
        """Extract logger comments that describe where the failure occurred."""
        logger_comments = []
        
        # Look for logger messages in captured logs
        if logs.get('captured_logs'):
            log_content = self._sanitize_text(logs['captured_logs'])
            # Extract meaningful log messages (typically contain file names, line numbers, step descriptions)
            log_lines = log_content.split('\n')
            for line in log_lines:
                # Look for lines that contain useful context about test execution
                if any(keyword in line.lower() for keyword in ['step', 'scenario', 'feature', 'error', 'fail', 'assert']):
                    # Clean up the log line and add it
                    clean_line = line.strip()
                    if clean_line and len(clean_line) > 10:  # Avoid very short/empty lines
                        logger_comments.append(clean_line)
        
        # Look for step-related information in other log sections
        for section_name, section_content in logs.items():
            if 'section_' in section_name and section_content:
                content = self._sanitize_text(section_content)
                if any(keyword in content.lower() for keyword in ['step', 'scenario', 'given', 'when', 'then']):
                    # This likely contains BDD step information
                    lines = content.split('\n')[:5]  # Take first few lines
                    for line in lines:
                        clean_line = line.strip()
                        if clean_line and len(clean_line) > 10:
                            logger_comments.append(clean_line)
        
        # Look for step information in failure details
        if failure_details.get('short_summary'):
            summary = self._sanitize_text(failure_details['short_summary'])
            # Extract file and line information
            if any(indicator in summary for indicator in ['.py:', 'line', 'step_defs', 'features']):
                logger_comments.append(f"Location: {summary}")
        
        # Limit and format the logger comments
        if logger_comments:
            # Remove duplicates while preserving order
            unique_comments = []
            seen = set()
            for comment in logger_comments:
                if comment not in seen:
                    unique_comments.append(comment)
                    seen.add(comment)
            
            # Limit to most relevant comments (max 5)
            relevant_comments = unique_comments[:5]
            
            # Format as bullet points
            formatted_comments = []
            for comment in relevant_comments:
                if len(comment) > 200:
                    comment = comment[:200] + "..."
                formatted_comments.append(f"• {comment}")
            
            return '\n'.join(formatted_comments)
        
        return ""
    
    def _extract_specific_error(self, failure_details):
        """Extract specific error information (assertions, exceptions)."""
        error_info = []
        
        # Priority 1: Assertion errors (most specific)
        if failure_details.get('assertion_error'):
            assertion_error = self._sanitize_text(failure_details['assertion_error'])
            # Clean up assertion error to show just the key information
            lines = assertion_error.split('\n')
            relevant_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('>') and not line.startswith('E   '):
                    # Skip pytest formatting lines, keep actual error content
                    if 'AssertionError' in line or 'assert' in line.lower() or 'expected' in line.lower():
                        relevant_lines.append(line)
            
            if relevant_lines:
                error_info.extend(relevant_lines[:3])  # Max 3 lines
        
        # Priority 2: Exception information from short summary
        if failure_details.get('short_summary') and not error_info:
            summary = self._sanitize_text(failure_details['short_summary'])
            # Look for exception types and messages
            if any(exc_type in summary for exc_type in ['Error', 'Exception', 'Failed']):
                # Extract the exception part
                lines = summary.split('\n')
                for line in lines:
                    if any(exc_type in line for exc_type in ['Error', 'Exception', 'Failed']):
                        error_info.append(line.strip())
                        break
        
        # Limit length and return
        if error_info:
            combined_error = '\n'.join(error_info)
            if len(combined_error) > 800:
                combined_error = combined_error[:800] + "... (truncated)"
            return combined_error
        
        return ""
    
    def _extract_verbose_logs(self, logs):
        """Extract verbose logs only when logger comments are insufficient."""
        verbose_content = []
        
        # Add captured stdout if it contains useful information
        if logs.get('captured_stdout'):
            stdout = self._sanitize_text(logs['captured_stdout'])
            if stdout and len(stdout.strip()) > 0:
                # Only include if it's not too verbose
                if len(stdout) > 300:
                    stdout = stdout[:300] + "... (truncated)"
                verbose_content.append(f"{{code:title=Output}}\n{stdout}\n{{code}}")
        
        # Add captured stderr if available
        if logs.get('captured_stderr'):
            stderr = self._sanitize_text(logs['captured_stderr'])
            if stderr and len(stderr.strip()) > 0:
                if len(stderr) > 300:
                    stderr = stderr[:300] + "... (truncated)"
                verbose_content.append(f"{{code:title=Error Output}}\n{stderr}\n{{code}}")
        
        return '\n\n'.join(verbose_content) if verbose_content else ""
    
    def _sanitize_text(self, text):
        """Sanitize text to avoid issues with Jira API."""
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Remove or replace problematic characters
        # Replace null bytes and other control characters
        text = text.replace('\x00', '')
        
        # Replace other control characters except newlines and tabs
        sanitized = ""
        for char in text:
            if ord(char) < 32 and char not in ['\n', '\t', '\r']:
                sanitized += ' '  # Replace with space
            else:
                sanitized += char
        
        return sanitized


def report_test_results(test_results):
    """
    Report test results to Jira.

    Args:
        test_results (list): List of test result dictionaries. Each dictionary should contain:
            - name (str): Name of the test
            - status (str): Test status ('PASS', 'FAIL', etc.)
            - comment (str, optional): Additional test details

    Returns:
        dict: The created test execution data from Jira, or None if an error occurred

    Example:
        >>> results = [
        ...     {'name': 'test_feature', 'status': 'PASS', 'comment': 'Test passed'},
        ...     {'name': 'another_test', 'status': 'FAIL', 'comment': 'Assertion failed'}
        ... ]
        >>> report_test_results(results)
    """
    if not test_results:
        print("No test results to report")
        return None

    if not isinstance(test_results, list):
        print(f"Expected list of test results, got {type(test_results).__name__}")
        return None

    try:
        reporter = JiraReporter()
        execution_result = reporter.create_test_execution(test_results)
        
        if not execution_result:
            print("Failed to create test execution in Jira")
            return None
            
        return execution_result
        
    except ValueError as ve:
        print(f"Configuration error: {str(ve)}")
    except requests.exceptions.RequestException as re:
        print(f"Network error while connecting to Jira: {str(re)}")
    except Exception as e:
        print(f"Unexpected error while reporting to Jira: {str(e)}")
        
    return None

