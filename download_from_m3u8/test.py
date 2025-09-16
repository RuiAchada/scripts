from seleniumwire import webdriver

driver = webdriver.Chrome()
driver.get('https://www.google.com')

for request in driver.requests:
    if request.response:
        print(
            request.url,
            request.response.status_code,
            request.response.headers['Content-Type']
        )

driver.quit()