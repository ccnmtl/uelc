from behave import then, when


@when(u'I visit "{url}"')
def i_visit(context, url):
    context.browser.visit(context.base_url + url)


@then(u'I get a {status_code} HTTP response')
def i_get_a_http_response(context, status_code):
    assert context.browser.status_code == int(status_code)
