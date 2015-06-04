Feature: Index Page
  Scenario: Index Page Load
    When I visit "/"
    Then I get a 200 HTTP response
