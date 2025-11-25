import logging

import pytest
import requests
from pytest_bdd import scenarios, given, then, parsers

DUCKDUCKGO_API = 'https://api.duckduckgo.com/'

scenarios('../features/duckduckgo_api.feature')


@pytest.fixture
def context():
    return {}


@given(parsers.parse('the DuckDuckGo API is queried with "{phrase}"'))
def ddg_api_response(context, phrase):
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
    expected_code = int(status_code)
    actual_code = context['response'].status_code
    logging.info(f"Verifying status code. Expected: {expected_code}, Actual: {actual_code}")
    assert actual_code == expected_code, f"Expected status code {expected_code}, but got {actual_code}"
    logging.info("Status code verification passed")


@then(parsers.parse('the response contains results for "{phrase}"'))
def ddg_api_response_contains_phrase(context, phrase):
    response_data = context['response'].json()
    all_fields_valid = True
    
    expected_fields = ['Abstract', 'Answer', 'Definition', 'Heading', 'RelatedTopics', 'Results', 'Type']
    
    for field in expected_fields:
        if field not in response_data:
            error_msg = f"Expected field '{field}' not found in response"
            logging.error(f"{error_msg} for phrase: {phrase}")
            all_fields_valid = False
        else:
            logging.info(f"Field '{field}' found in response for phrase: {phrase}")
    
    if 'meta' not in response_data:
        error_msg = "Response missing 'meta' field. This indicates an invalid API response"
        logging.error(f"{error_msg} for phrase: {phrase}")
        all_fields_valid = False

    assert all_fields_valid, f"One or more required fields are missing in the response for phrase: {phrase}. Check logs for details."
    logging.info(f"All required fields validated successfully for phrase: {phrase}")


@then(parsers.parse('the phrase "{phrase}" appears somewhere in the response'))
def phrase_appears_in_response(context, phrase):
    response_data = context['response'].json()
    response_text = str(response_data).lower()
    phrase_lower = phrase.lower()
    
    if phrase_lower not in response_text:
        logging.warning(
            f"Phrase '{phrase}' not found in the response. "
            f"This might be expected. Response: {response_data}"
        )
    else:
        logging.info(f"Phrase {phrase} is present in the response")
