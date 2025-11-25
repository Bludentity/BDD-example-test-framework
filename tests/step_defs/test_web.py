import os
import time

import pytest
import requests
from pytest_bdd import scenarios, given, when, then, parsers
from requests.exceptions import RequestException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..conftest import SCREENSHOT_DIR

scenarios('../features/web.feature')


def perform_search(browser, search_text, context):
    search_box = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.NAME, "q"))
    )

    search_box.click()
    search_box.clear()
    WebDriverWait(browser, 10).until(EC.visibility_of(search_box))
    
    if len(search_text) > 100:
        browser.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, search_box, search_text)
    else:
        search_box.send_keys(search_text)

    context['search_text'] = search_text

    search_box.send_keys(Keys.RETURN)

    base_timeout = 30 if len(search_text) > 100 else 20
    network_latency = context.get('network_latency') or 0
    extra_buffer = 10 if network_latency > 1.5 else 5 if network_latency > 0.8 else 0
    wait_timeout = base_timeout + extra_buffer

    print(
        f"Waiting up to {wait_timeout}s for results (base: {base_timeout}s, "
        f"latency: {network_latency:.2f}s, extra buffer: {extra_buffer}s)"
    )

    WebDriverWait(browser, wait_timeout).until(
        EC.any_of(
            EC.url_contains("?q="),
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='result']")),
            EC.presence_of_element_located((By.ID, "links")),
            EC.presence_of_element_located((By.CLASS_NAME, "results--main"))
        )
    )

    context['result_wait_timeout'] = wait_timeout


@pytest.fixture
def search_context(browser):
    return {'browser': browser, 'result_wait_timeout': None, 'network_latency': None}

@given('the DuckDuckGo homepage is displayed')
def navigate_to_homepage(browser, search_context, request):
    """Navigate to DuckDuckGo, verifying connectivity first."""
    test_name = request.node.name
    print(f"\n=== Starting test: {test_name} ===")

    try:
        print("Checking network connectivity to DuckDuckGo...")
        start_time = time.perf_counter()
        response = requests.get("https://duckduckgo.com", timeout=5)
        response.raise_for_status()
        latency = time.perf_counter() - start_time
        search_context['network_latency'] = latency
        print(f"Network check succeeded in {latency:.2f}s (status {response.status_code})")
    except RequestException as connectivity_error:
        raise pytest.skip(f"Skipping test due to connectivity issue: {connectivity_error}")

    try:
        print("Navigating to DuckDuckGo...")
        browser.get("https://duckduckgo.com")

        print("Waiting for page to load...")
        WebDriverWait(browser, 15).until(
            lambda d: "DuckDuckGo" in d.title
        )
        print(f"Page title: {browser.title}")

        search_context['browser'] = browser
        print("Successfully loaded DuckDuckGo homepage")
    except Exception as e:
        error_screenshot = os.path.join(SCREENSHOT_DIR, f"homepage_error_{int(time.time())}.png")
        try:
            browser.save_screenshot(error_screenshot)
            print(f"Screenshot saved to {error_screenshot}")
        except Exception as se:
            print(f"Failed to save screenshot: {se}")

        print(f"Error loading page: {str(e)}")
        print(f"Current URL: {browser.current_url}")
        print(f"Page source: {browser.page_source[:1000]}...")
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

    print(f"Current URL: {browser.current_url}")
    print(f"Page title: {browser.title}")
    
    result_selectors = [
        (By.TAG_NAME, "body"),
        (By.ID, "react-layout"),
        (By.CSS_SELECTOR, "[data-testid='results']"),
        (By.ID, "links"),
        (By.CLASS_NAME, "react-results--main"),
        (By.CLASS_NAME, "results--main"),
        (By.CLASS_NAME, "results")
    ]
    
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
        search_text = search_context.get('search_text', '')
        timeout = 20 if len(search_text) > 100 else 15
        print(f"Waiting for results container (timeout: {timeout}s)...")
        results_container = WebDriverWait(browser, timeout).until(
            any_result_container_present,
            message="Could not find any result container"
        )
        
        container_text = results_container.text.lower()
        print(f"Container text (first 500 chars): {container_text[:500]}...")

        if phrase_lower in container_text:
            print(f"Found phrase '{phrase}' in results container")
            return

        print("Checking full page source...")
        page_source = browser.page_source.lower()
        if phrase_lower in page_source:
            print(f"Found phrase '{phrase}' in full page source")
            return

        error_screenshot = os.path.join(SCREENSHOT_DIR, f"search_error_{int(time.time())}.png")
        browser.save_screenshot(error_screenshot)
        print(f"Screenshot saved to {error_screenshot}")

        assert False, (
            f"Phrase '{phrase}' not found in search results."
        )

    except Exception as e:
        error_screenshot = os.path.join(SCREENSHOT_DIR, f"search_error_{int(time.time())}.png")
        browser.save_screenshot(error_screenshot)
        print(f"Screenshot saved to {error_screenshot}")

        print(f"Page source at time of error (first 2000 chars): {browser.page_source[:2000]}...")
        raise AssertionError(
            f"Error while searching for results: {str(e)}."
        ) from e

@then(parsers.parse('one of the results contains "{expected_text}"'))
def verify_result_contains_text(search_context, expected_text):
    """Verify that at least one search result contains the expected text."""
    print(f"\nVerifying one of the results contains: '{expected_text}'")
    browser = search_context['browser']
    expected_lower = expected_text.lower()

    print(f"Current URL: {browser.current_url}")
    print(f"Page title: {browser.title}")
    
    result_selectors = [
        (By.TAG_NAME, "body"),
        (By.ID, "react-layout"),
        (By.CSS_SELECTOR, "[data-testid='results']"),
        (By.ID, "links"),
        (By.CLASS_NAME, "react-results--main"),
        (By.CLASS_NAME, "results--main"),
        (By.CLASS_NAME, "results"),
        (By.CSS_SELECTOR, "article"),
        (By.CSS_SELECTOR, ".result"),
        (By.CSS_SELECTOR, "[data-testid='result']")
    ]
    
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
        search_text = search_context.get('search_text', '')
        timeout = 20 if len(search_text) > 100 else 15
        print(f"Waiting for results container (timeout: {timeout}s)...")
        results_container = WebDriverWait(browser, timeout).until(
            any_result_container_present,
            message="Could not find any result container"
        )
        
        container_text = results_container.text.lower()
        print(f"Container text (first 500 chars): {container_text[:500]}...")
        
        if expected_lower in container_text:
            print(f"Found expected text '{expected_text}' in results container")
            return
            
        print("Checking full page source...")
        page_source = browser.page_source.lower()
        if expected_lower in page_source:
            print(f"Found expected text '{expected_text}' in full page source")
            return
            
        error_screenshot = os.path.join(SCREENSHOT_DIR, f"search_error_{int(time.time())}.png")
        browser.save_screenshot(error_screenshot)
        print(f"Screenshot saved to {error_screenshot}")

        assert False, (
            f"Expected text '{expected_text}' not found in search results."
        )
        
    except Exception as e:
        error_screenshot = os.path.join(SCREENSHOT_DIR, f"search_error_{int(time.time())}.png")
        browser.save_screenshot(error_screenshot)
        print(f"Screenshot saved to {error_screenshot}")

        print(f"Page source at time of error (first 2000 chars): {browser.page_source[:2000]}...")
        raise AssertionError(
            f"Error while searching for results: {str(e)}."
        ) from e
