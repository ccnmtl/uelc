Feature: Admin
  Scenario: Access the admin panel
    Given I am signed in as a "admin"
    When I visit "/"
    Then I see the text "User001's Start Page"

    When I visit "/pages/doesnt-exist/"
    Then I see the text "No hierarchy named doesnt-exist found"

    When I visit "/pages/case-one/"
    Then I see the text "Test Edit Facilitator Scratchpad"

    When I visit "/uelcadmin/"
    Then I see the text "Management Panel"

    When I click the link "Case"
    Then I see the text "Add and Edit Cases"

    When I click the link "Cohort"
    Then I see the text "Create and Edit Cohorts"

    When I click the link "Users"
    Then I see the text "Create User"

  Scenario: Create a user
    Given I am signed in as a "admin"
    When I visit "/uelcadmin/user/"
    When I click the button "Create User"

    When I click the user modal submit button
    Then I see the text "This field is required."

    When I fill out the create user form for user "testuser"
    When I click the user modal submit button
    # TODO: why doesn't this pass?
    # Then the user "testuser" exists
