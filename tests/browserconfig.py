from selenium.webdriver.chrome.options import Options


# Enter the name of your preferred browser (Firefox, Chrome, Safari)
select_browser = "Chrome"

browser_options = Options()
# Run browser in headless mode - make next line a comment to view browser GUI
browser_options.add_argument("--headless")
browser_options.add_argument("--no-sandbox")
browser_options.add_argument("--disable-dev-shm-usage")