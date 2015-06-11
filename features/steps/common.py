import urlparse
from behave import then, when


@when(u'I click the case button')
def i_click_the_case_button(context):
    context.browser.find_by_css('.case-index-list li>a').first.click()


@when(u'I click the button "{text}"')
def i_click_the_button(context, text):
    context.browser.find_by_text(text).first.click()


@when(u'I click the link "{text}"')
def i_click_the_link(context, text):
    context.browser.find_link_by_partial_text(text).first.click()


@when(u'I visit "{url}"')
def i_visit(context, url):
    context.browser.visit(urlparse.urljoin(context.base_url, url))


@then(u'I get a {status_code} HTTP response')
def i_get_a_http_response(context, status_code):
    assert context.browser.status_code == int(status_code)


@then(u'I see the text "{text}"')
def i_see_the_text(context, text):
    assert context.browser.is_text_present(text)


@then(u'My URL ends with "{url}"')
def my_url_ends_with(context, url):
    assert context.browser.url.endswith(url)
