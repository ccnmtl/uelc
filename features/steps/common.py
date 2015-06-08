import urlparse
from behave import then, when


@when(u'I visit "{url}"')
def i_visit(context, url):
    context.browser.visit(urlparse.urljoin(context.base_url, url))


@then(u'I get a {status_code} HTTP response')
def i_get_a_http_response(context, status_code):
    assert context.browser.status_code == int(status_code)


@then(u'I see the text "{text}"')
def i_see_the_text(context, text):
    assert context.browser.is_text_present(text)
