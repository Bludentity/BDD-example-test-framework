Feature: Cucumber basket
  As a gardener,
  I want to carry cucumbers in a basket,
  So that I don't drop them all.

  Scenario Outline: Add cucumbers to a basket
    Given the basket has "<initial>" cucumbers
    When "<count>" cucumbers are added to the basket
    Then the basket contains "<total>" cucumbers

    Examples: Amounts of cucumbers
    | initial | count | total |
    | 2       | 4     | 6     |
    | 3       | 5     | 8     |
    | 4       | 6     | 10    |
    | 0       | 7     | 7     |


  Scenario: Remove cucumbers from a basket
    Given the basket has "8" cucumbers
    When "3" cucumbers are removed from the basket
    Then the basket contains "5" cucumbers