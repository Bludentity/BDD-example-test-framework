from selenium.webdriver.chrome.options import Options


# Choose your browser: "Chrome", "Firefox", or "Safari"
select_browser = "Chrome"

# Browser options
browser_options = Options()
# Uncomment the next line to run tests without opening browser window
# browser_options.add_argument("--headless")
browser_options.add_argument("--no-sandbox")
browser_options.add_argument("--disable-dev-shm-usage")
