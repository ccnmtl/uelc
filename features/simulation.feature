Feature: Simulation
  Scenario: Go through the simulation
    Given I am signed in as a "group user"
    When I visit "/"
    Then I see the text "User001's Start Page"
    Then I see the text "Group Leader Case List"

    When I click the case button
    Then I see the text "Home"
    Then I see the text "Intro"
    Then I see the text "Challenges"
    Then I see the text "Testing in Applegate"
    Then I see the text "Your First Decision"

    When I click the link "Testing in Applegate"
    Then My URL ends with "/testing-in-applegate/"

    # TODO: figure out why the decision block freezes here
    # When I click the link "Your First Decision"
