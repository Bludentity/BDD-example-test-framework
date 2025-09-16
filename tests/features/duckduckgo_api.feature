Feature: DuckDuckGo Instant Answer API
  As an application developer,
  I want to get instant answers for search terms using REST API,
  So that my app can get answers anywhere.


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

