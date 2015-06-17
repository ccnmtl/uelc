Feature: Simulation
  Scenario: Go through the simulation
    Given I am signed in as a "group user"
    When I visit "/pages/case-test/"
    Then my URL ends with "/pages/case-test/part-1/home/"

    When I click the case button
    Then I see the text "Home"
    Then I see the text "Intro"
    Then I see the text "Challenges"
    Then I see the text "Testing in Applegate"
    Then I see the text "Your First Decision"

    When I click the link "Testing in Applegate"
    Then my URL ends with "/testing-in-applegate/"

    When I click the link "Your First Decision"
    Then my URL ends with "/part-1/your-first-decision/"
    Then I see the text "Choice 1: Full Disclosure"
    When I select the first radio option
    When I click the button "Submit Decision"
    Then my URL ends with "/part-1/your-first-decision/curve-ball/"
