import os
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


def select_browser():
    browser_name = os.environ.get('BROWSER', 'Chrome').strip().lower()
    valid_browsers = {'chrome': 'Chrome', 'firefox': 'Firefox', 'edge': 'Edge'}
    return valid_browsers.get(browser_name, 'Chrome')


def browser_options(browser_name):
    browser_name = browser_name.lower()
    
    if browser_name == 'firefox':
        options = FirefoxOptions()
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", False)
        options.set_preference("browser.cache.offline.enable", False)
        options.set_preference("network.http.use-cache", False)
        
        firefox_bin = os.environ.get('FIREFOX_BIN')
        if firefox_bin and os.path.exists(firefox_bin):
            options.binary_location = firefox_bin
            
    elif browser_name == 'edge':
        options = EdgeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    else:
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    
    if os.environ.get('HEADLESS', 'false').lower() == 'true':
        options.add_argument("--headless")
    
    return options
