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
    Then I see the css selector ".alert.alert-danger"
    Then my URL ends with "/part-1/your-first-decision/"

    When I sign out
    When I sign in as a "admin"
    When I attach the admins to the group user's cohort
    When I visit "/pages/case-test/facilitator/"
    Then I see the text "Case Control for case-test"
    Then I see the css selector ".gate-section-list"
    Then there are no curveball submissions

    When I click the button "Commit"
    Then I see the text "Are you sure?"
    When I click the button "Yes. Set it."
    Then I see the text "Choice 1:"
    Then a curveball submission exists
