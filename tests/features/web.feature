Feature: DuckDuckGo Search
  As a web user,
  I want to find information on the web,
  So that I can learn new things.

  Background:
    Given the DuckDuckGo homepage is displayed


   Scenario Outline: Basic DuckDuckGo Search
      When the user searches for "<phrase>"
      Then the search results should contain "<phrase>"

      Examples:
      | phrase |
      | panda  |
      | python |
      | alvin  |


   Scenario Outline: Lengthy DuckDuckGo search
      When the user searches for the lengthy phrase
      Then one of the results contains "<expected_text>"

     Examples:
     | expected_text |
     | Independence  |
     | human events  |