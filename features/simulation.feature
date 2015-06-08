Feature: Simulation
  Scenario: Go through the simulation
    Given I am signed in as a group user
    When I visit "/"
    Then I see the text "User001's Start Page"
    Then I see the text "It looks like you have not been assigned to a cohort"
