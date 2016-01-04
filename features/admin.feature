Feature: Admin
  Scenario: Access the admin panel
    Given I am signed in as a "admin"
    When I visit "/"
    Then I see the text "Hello"

    When I visit "/pages/doesnt-exist/"
    Then I see the text "No hierarchy with url /pages/doesnt-exist/ found"

    When I visit "/pages/case-test/"
    Then I see the text "Test Edit Facilitator Scratchpad"

    When I visit "/uelcadmin/"
    Then I see the text "Management Panel"

    When I click the link "Case"
    Then I see the text "Add and Edit Cases"

    When I click the link "Cohort"
    Then I see the text "Create and Edit Cohorts"

    When I click the link "Users"
    Then I see the text "Create User"

  Scenario: Attempt to attach two cases to one hierarchy
    Given I am signed in as a "admin"
    When I visit "/uelcadmin/case/"
    When I click the button "Add Case"
    When I fill out the create case form for "created_case"
    When I click the modal submit button for "#cases"
    Then I see the text "error"
    Then I see the text "Case already exists!"

  Scenario: Create a case
    Given I am signed in as a "admin"
    When I visit "/uelcadmin/case/"
    When I click the button "Add Hierarchy Item"
    When I click the modal submit button for "#add-hierarchy-form-modal"
    Then I see the text "This field is required"
    Then the hierarchy "created_hierarchy" doesn't exist

    When I fill out the create hierarchy form for "created_hierarchy"
    When I click the modal submit button for "#add-hierarchy-form-modal"
    Then the hierarchy "created_hierarchy" exists

    When I click the button "Add Case"
    When I fill out the create case form for "created_case"
    When I click the modal submit button for "#cases"
    Then I don't see the text "error"
    Then I don't see the text "Case already exists!"
    Then the case "created_case" exists

  # Scenario: Add a hierarchy item

  # Scenario: Delete a hierarchy item

  # Scenario: Create a cohort
  #   Given I am signed in as a "admin"
  #   When I visit "/uelcadmin/cohort/"

  Scenario: Create a user
    Given I am signed in as a "admin"
    When I visit "/uelcadmin/user/"
    When I click the button "Create User"

    When I click the modal submit button for "#users"
    Then I see the text "This field is required."

    When I fill out the create user form for "testuser"
    When I click the modal submit button for "#users"
    Then the user "testuser" exists
