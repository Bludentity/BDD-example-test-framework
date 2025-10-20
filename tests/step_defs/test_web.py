import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from ..conftest import SCREENSHOT_DIR

# Import the scenarios from the feature file
scenarios('../features/web.feature')


def perform_search(browser, search_text, context):
    """Helper function to perform search using standard Selenium WebDriver methods."""
    # Find the search box and enter text using ActionChains for more reliable input
    search_box = WebDriverWait(browser, 10).until(  # Reduced from 15 to 10 seconds
        EC.presence_of_element_located((By.NAME, "q"))
    )
    
    # Clear any existing text in the search box
    search_box.clear()
    
    # For very long search text, use direct send_keys instead of ActionChains
    # to avoid timeout issues with character-by-character typing
    if len(search_text) > 100:
        # For long text, use direct input method which is faster
        search_box.send_keys(search_text)
    else:
        # Use ActionChains for shorter text for more reliable input
        actions = ActionChains(browser)
        actions.move_to_element(search_box)
        actions.click()
        actions.send_keys(search_text)
        actions.perform()
    
    # Store the search text in the context for later verification
    context['search_text'] = search_text
    
    # Submit the search form - use a more robust method
    try:
        search_box.submit()
    except Exception as e:
        print(f"Submit failed, trying alternative method: {str(e)}")
        # Alternative: find and click the search button
        try:
            search_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
            search_button.click()
        except Exception as e2:
            print(f"Search button click failed: {str(e2)}")
            # Final fallback: press Enter key on a fresh element
            try:
                # Re-find the search box to avoid stale element issues
                fresh_search_box = browser.find_element(By.NAME, "q")
                fresh_search_box.send_keys("\n")
            except Exception as e3:
                print(f"Enter key fallback failed: {str(e3)}")
                # Last resort: use JavaScript to submit
                browser.execute_script("document.querySelector('form').submit();")
    
    # Wait for the search results to load with optimized timeout for complex searches
    if len(search_text) > 100:
        time.sleep(3)  # Reduced wait for complex searches (was 5)
    else:
        time.sleep(1)  # Reduced wait for simple searches (was 2)


@pytest.fixture
def search_context(browser):
    """Context fixture to store search data between steps."""
    return {'browser': browser}

@given('the DuckDuckGo homepage is displayed')
def navigate_to_homepage(browser, search_context, request):
    """Navigate to the DuckDuckGo homepage and verify it's loaded."""
    test_name = request.node.name
    print(f"\n=== Starting test: {test_name} ===")

    try:
        # Navigate to DuckDuckGo
        print("Navigating to DuckDuckGo...")
        browser.get("https://duckduckgo.com")

        # Wait for the page to load
        print("Waiting for page to load...")
        WebDriverWait(browser, 10).until(  # Reduced from 15 to 10 seconds
            lambda d: "DuckDuckGo" in d.title
        )
        print(f"Page title: {browser.title}")

        # Save browser to context
        search_context['browser'] = browser
        print("Successfully loaded DuckDuckGo homepage")
    except Exception as e:
        # Take screenshot on failure
        error_screenshot = os.path.join(SCREENSHOT_DIR, f"homepage_error_{int(time.time())}.png")
        try:
            browser.save_screenshot(error_screenshot)
            print(f"Screenshot saved to {error_screenshot}")
        except Exception as se:
            print(f"Failed to save screenshot: {se}")

        print(f"Error loading page: {str(e)}")
        print(f"Current URL: {browser.current_url}")
        print(f"Page source: {browser.page_source[:1000]}...")  # First 1000 chars
        raise

@when(parsers.parse('the user searches for "{phrase}"'))
def search_for_phrase(search_context, phrase):
    """Perform a search for the given phrase."""
    print(f"\nSearching for phrase: '{phrase}'")
    browser = search_context['browser']

    try:
        perform_search(browser, phrase, search_context)
        print("Search performed successfully")
    except Exception as e:
        # Take screenshot on failure
        error_screenshot = os.path.join(SCREENSHOT_DIR, f"search_error_{int(time.time())}.png")
        try:
            browser.save_screenshot(error_screenshot)
            print(f"Screenshot saved to {error_screenshot}")
        except Exception as se:
            print(f"Failed to save screenshot: {se}")

        print(f"Search failed: {str(e)}")
        print(f"Current URL: {browser.current_url}")
        print(f"Page source: {browser.page_source[:1000]}...")
        raise

@when('user searches for the phrase:')
def search_for_multiline_phrase(search_context, docstring):
    """Perform a search for a multiline phrase (docstring)."""
    print(f"\nSearching for multiline phrase (length: {len(docstring)} chars)")
    print(f"First 100 chars: {docstring[:100]}...")
    browser = search_context['browser']

    try:
        perform_search(browser, docstring, search_context)
        print("Multiline search performed successfully")
    except Exception as e:
        # Take screenshot on failure
        error_screenshot = os.path.join(SCREENSHOT_DIR, f"multiline_search_error_{int(time.time())}.png")
        try:
            browser.save_screenshot(error_screenshot)
            print(f"Screenshot saved to {error_screenshot}")
        except Exception as se:
            print(f"Failed to save screenshot: {se}")

        print(f"Multiline search failed: {str(e)}")
        print(f"Current URL: {browser.current_url}")
        print(f"Page source: {browser.page_source[:1000]}...")
        raise

@then(parsers.parse('the search results should contain "{phrase}"'))
def verify_results_contain_phrase(search_context, phrase):
    """Verify that the search results contain the specified phrase."""
    print(f"\nVerifying results contain: '{phrase}'")
    browser = search_context['browser']
    phrase_lower = phrase.lower()

    # Print current URL and title for debugging
    print(f"Current URL: {browser.current_url}")
    print(f"Page title: {browser.title}")
    
    # Define multiple possible selectors for the results container
    # Ordered by frequency of success in actual test runs
    result_selectors = [
        (By.TAG_NAME, "body"),  # Most reliable fallback - found in most runs
        (By.ID, "react-layout"),  # Often present in DuckDuckGo's React-based layout
        (By.CSS_SELECTOR, "[data-testid='results']"),  # Modern DuckDuckGo selector
        (By.ID, "links"),  # Classic DuckDuckGo results container
        (By.CLASS_NAME, "react-results--main"),  # React-based results
        (By.CLASS_NAME, "results--main"),  # Main results container
        (By.CLASS_NAME, "results")  # Generic results container
    ]
    
    # Custom expected condition to wait for any result container
    def any_result_container_present(driver):
        for by, selector in result_selectors:
            try:
                element = driver.find_element(by, selector)
                if element.is_displayed():
                    print(f"Found results container with: {by}={selector}")
                    return element
            except Exception as e:
                print(f"Could not find results container with {by}={selector}: {str(e)}")
                continue
        print("No results container found with any selector")
        return False
    
    try:
        # Wait for any result container to be present with optimized timeout for complex searches
        search_text = search_context.get('search_text', '')
        timeout = 20 if len(search_text) > 100 else 15  # Reduced timeouts (was 30/20)
        print(f"Waiting for results container (timeout: {timeout}s)...")
        results_container = WebDriverWait(browser, timeout).until(
            any_result_container_present,
            message="Could not find any result container"
        )
        
        # Get the visible text from the results container
        container_text = results_container.text.lower()
        print(f"Container text (first 500 chars): {container_text[:500]}...")
        
        # Check if the phrase is in the results container text
        if phrase_lower in container_text:
            print(f"Found phrase '{phrase}' in results container")
            return
            
        # Fallback: Check the entire page source if not found in the container
        print("Checking full page source...")
        page_source = browser.page_source.lower()
        if phrase_lower in page_source:
            print(f"Found phrase '{phrase}' in full page source")
            return
            
        # If we get here, the phrase wasn't found
        error_screenshot = os.path.join(SCREENSHOT_DIR, f"search_error_{int(time.time())}.png")
        browser.save_screenshot(error_screenshot)
        print(f"Screenshot saved to {error_screenshot}")

        assert False, (
            f"Phrase '{phrase}' not found in search results."
        )

    except Exception as e:
        # Save screenshot for Jira attachment
        error_screenshot = os.path.join(SCREENSHOT_DIR, f"search_error_{int(time.time())}.png")
        browser.save_screenshot(error_screenshot)
        print(f"Screenshot saved to {error_screenshot}")

        print(f"Page source at time of error: {browser.page_source[:2000]}...")  # Print first 2000 chars of page source
        raise AssertionError(
            f"Error while searching for results: {str(e)}."
        ) from e

@then(parsers.parse('one of the results contains "{expected_text}"'))
def verify_result_contains_text(search_context, expected_text):
    """Verify that at least one search result contains the expected text."""
    print(f"\nVerifying one of the results contains: '{expected_text}'")
    browser = search_context['browser']
    expected_lower = expected_text.lower()

    # Print current URL and title for debugging
    print(f"Current URL: {browser.current_url}")
    print(f"Page title: {browser.title}")
    
    # Define possible result container selectors with more comprehensive list
    # Ordered by frequency of success in actual test runs for faster execution
    result_selectors = [
        (By.TAG_NAME, "body"),  # Most reliable fallback - found in most runs
        (By.ID, "react-layout"),  # Often present in DuckDuckGo's React-based layout
        (By.CSS_SELECTOR, "[data-testid='results']"),  # Modern DuckDuckGo selector
        (By.ID, "links"),  # Classic DuckDuckGo results container
        (By.CLASS_NAME, "react-results--main"),  # React-based results
        (By.CLASS_NAME, "results--main"),  # Main results container
        (By.CLASS_NAME, "results"),  # Generic results container
        (By.CSS_SELECTOR, "article"),  # Article-based results
        (By.CSS_SELECTOR, ".result"),  # Individual result items
        (By.CSS_SELECTOR, "[data-testid='result']")  # Modern individual result selector
    ]
    
    # Custom expected condition to wait for any result container
    def any_result_container_present(driver):
        for by, selector in result_selectors:
            try:
                element = driver.find_element(by, selector)
                if element.is_displayed():
                    print(f"Found results container with: {by}={selector}")
                    return element
            except Exception as e:
                print(f"Could not find results container with {by}={selector}: {str(e)}")
                continue
        print("No results container found with any selector")
        return False
    
    try:
        # Wait for any result container to be present with optimized timeout for complex searches
        search_text = search_context.get('search_text', '')
        timeout = 20 if len(search_text) > 100 else 15  # Reduced timeouts (was 30/20)
        print(f"Waiting for results container (timeout: {timeout}s)...")
        results_container = WebDriverWait(browser, timeout).until(
            any_result_container_present,
            message="Could not find any result container"
        )
        
        # Get the visible text from the results container
        container_text = results_container.text.lower()
        print(f"Container text (first 500 chars): {container_text[:500]}...")
        
        # Check if the expected text is in the results container text
        if expected_lower in container_text:
            print(f"Found expected text '{expected_text}' in results container")
            return
            
        # Fallback: Check the entire page source if not found in the container
        print("Checking full page source...")
        page_source = browser.page_source.lower()
        if expected_lower in page_source:
            print(f"Found expected text '{expected_text}' in full page source")
            return
            
        # If we get here, the expected text wasn't found
        error_screenshot = os.path.join(SCREENSHOT_DIR, f"search_error_{int(time.time())}.png")
        browser.save_screenshot(error_screenshot)
        print(f"Screenshot saved to {error_screenshot}")

        assert False, (
            f"Expected text '{expected_text}' not found in search results."
        )
        
    except Exception as e:
        # Save screenshot for Jira attachment
        error_screenshot = os.path.join(SCREENSHOT_DIR, f"search_error_{int(time.time())}.png")
        browser.save_screenshot(error_screenshot)
        print(f"Screenshot saved to {error_screenshot}")

        print(f"Page source at time of error: {browser.page_source[:2000]}...")  # Print first 2000 chars of page source
        raise AssertionError(
            f"Error while searching for results: {str(e)}."
        ) from e
