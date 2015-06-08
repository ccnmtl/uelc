Feature: Admin
  Scenario: Access the admin panel
    Given I am signed in as a "admin"
    When I visit "/"
    Then I see the text "User001's Start Page"

    When I visit "/pages/case-one-facilitator/"
    Then I see the text "No hierarchy named case-one-facilitator found"
