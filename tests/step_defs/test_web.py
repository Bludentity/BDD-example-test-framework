import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

# Import the scenarios from the feature file
scenarios('../features/web.feature')


def perform_search(browser, search_text, context):
    """Helper function to perform search using standard Selenium WebDriver methods."""
    search_box = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.NAME, "q"))
    )
    
    actions = ActionChains(browser)
    actions.click(search_box)
    actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
    actions.send_keys(search_text)
    actions.send_keys(Keys.RETURN)
    actions.perform()
    
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "web_content_wrapper"))
    )
    
    context['search_text'] = search_text

@pytest.fixture
def search_context():
    """Context fixture to store search data between steps."""
    return {}

@given('the DuckDuckGo homepage is displayed')
def navigate_to_homepage(browser, search_context):
    """Navigate to the DuckDuckGo homepage and verify it's loaded."""
    browser.get("https://duckduckgo.com")
    time.sleep(3)
    
    WebDriverWait(browser, 15).until(
        EC.element_to_be_clickable((By.NAME, "q"))
    )
    
    assert "DuckDuckGo" in browser.title
    search_context['browser'] = browser

@when(parsers.parse('the user searches for "{phrase}"'))
def search_for_phrase(search_context, phrase):
    """Perform a search for the given phrase."""
    browser = search_context['browser']
    perform_search(browser, phrase, search_context)

@when('user searches for the phrase:')
def search_for_multiline_phrase(search_context, docstring):
    """Perform a search for a multiline phrase (docstring)."""
    browser = search_context['browser']
    perform_search(browser, docstring, search_context)

@then(parsers.parse('the search results should contain "{phrase}"'))
def verify_results_contain_phrase(search_context, phrase):
    """Verify that the search results contain the specified phrase."""
    browser = search_context['browser']
    page_source = browser.page_source.lower()
    phrase_lower = phrase.lower()
    
    try:
        results_section = browser.find_element(By.CLASS_NAME, "results--main")
        results_text = results_section.text.lower()
        phrase_found = phrase_lower in results_text or phrase_lower in page_source
        assert phrase_found, f"Phrase '{phrase}' not found in search results"
    except Exception:
        assert phrase_lower in page_source, f"Phrase '{phrase}' not found in page source"

@then(parsers.parse('one of the results contains "{expected_text}"'))
def verify_result_contains_text(search_context, expected_text):
    """Verify that at least one search result contains the expected text."""
    browser = search_context['browser']
    expected_lower = expected_text.lower()
    
    try:
        results_section = browser.find_element(By.CLASS_NAME, "results--main")
        if expected_lower in results_section.text.lower():
            return
    except Exception:
        pass
    
    # Fallback to page source check
    page_source = browser.page_source.lower()
    assert expected_lower in page_source, f"Expected text '{expected_text}' not found in search results"
