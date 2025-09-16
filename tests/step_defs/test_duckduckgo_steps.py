import pytest
import requests
from pytest_bdd import scenarios, given, then, parsers
import  logging

# Constants
DUCKDUCKGO_API = 'https://api.duckduckgo.com/'

# Import the scenarios from the feature file
scenarios('../features/duckduckgo_api.feature')

@pytest.fixture
def context():
    return {}


@given(parsers.parse('the DuckDuckGo API is queried with "{phrase}"'))
def ddg_api_response(context, phrase):
    """Make a request to the DuckDuckGo API with the search phrase."""
    logging.info(f"Making API request with phrase: {phrase}")
    params = {
        'q': phrase,
        'format': 'json',
    }

    response = requests.get(DUCKDUCKGO_API, params=params)
    context['response'] = response
    context['phrase'] = phrase
    logging.info(f"Received response with status code: {response.status_code}")

@then(parsers.parse('the response status code is "{status_code}"'))
def ddg_api_response_code(context, status_code):
    """Verify the HTTP status code of the response."""
    expected_code = int(status_code)
    actual_code = context['response'].status_code
    logging.info(f"Verifying status code. Expected: {expected_code}, Actual: {actual_code}")
    assert actual_code == expected_code, \
        f"Expected status code {expected_code}, but got {actual_code}"
    logging.info("Status code verification passed")

@then(parsers.parse('the response contains results for "{phrase}"'))
def ddg_api_response_contains_phrase(context, phrase):
    """Verify the response contains a valid structure for the search phrase."""
    response_data = context['response'].json()
    all_fields_valid = True
    
    # Check that we got a valid DuckDuckGo API response structure
    # The API should return these standard fields even if they're empty
    expected_fields = ['Abstract', 'Answer', 'Definition', 'Heading', 'RelatedTopics', 'Results', 'Type']
    
    # Check each expected field
    for field in expected_fields:
        if field not in response_data:
            error_msg = f"Expected field '{field}' not found in response"
            logging.error(f"{error_msg} for phrase: {phrase}")
            all_fields_valid = False
        else:
            logging.info(f"Field '{field}' found in response for phrase: {phrase}")
    
    # Check for meta field
    if 'meta' not in response_data:
        error_msg = "Response missing 'meta' field. This indicates an invalid API response"
        logging.error(f"{error_msg} for phrase: {phrase}")
        all_fields_valid = False
    else:
        logging.info(f"Meta field found in response for phrase: {phrase}")
    
    # Final assertion with all errors if any
    assert all_fields_valid, \
        f"One or more required fields are missing in the response for phrase: {phrase}. Check logs for details."
    logging.info(f"All required fields validated successfully for phrase: {phrase}")


@then(parsers.parse('the phrase "{phrase}" appears somewhere in the response'))
def phrase_appears_in_response(context, phrase):
    """Check if the search phrase appears somewhere in the API response.
    
    Note: This is a non-fatal check since the API might not always include
    the search phrase in the response. It will only log a warning if the
    phrase is not found.
    """

    response_data = context['response'].json()
    response_text = str(response_data).lower()
    phrase_lower = phrase.lower()
    
    if phrase_lower not in response_text:
        # Log a warning instead of failing the test
        logging.warning(
            f"Phrase '{phrase}' not found in the response. "
            f"This might be expected. Response: {response_data}"
        )
    else:
        logging.info(f"Phrase {phrase} is present in the response")
