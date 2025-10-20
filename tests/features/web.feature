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
      When user searches for the phrase:
      """
      When in the course of human events, it becomes necessary for one people
      to dissolve the political bands which have connected them with another,
      and to assume among the powers of the earth, the separate and equal station
      to which the Laws of Nature and of Nature's God entitle them, a decent respect
      to the opinions of mankind requires that they should declare the causes
      which impel them to the separation.
      """
      Then one of the results contains "<expected_text>"

     Examples:
     | expected_text |
     | Independence  |
     | human events  |