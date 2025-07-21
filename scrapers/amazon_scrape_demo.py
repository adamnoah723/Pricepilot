import requests
from rich import print as print, print_json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from fake_useragent import UserAgent
from selenium.common.exceptions import WebDriverException
import time
import random
import json
import sys
import tempfile
import os

class SeleniumFetcher:
    def __init__(self, is_headless = False):
        self.driver = None
        self.is_headless = is_headless
        self.fetch_count = 0

    def initialize_human_browser_history(self):
        #self.fetch('https://www.reddit.com/r/neovim/comments/1ec871j/i_didnt_quite_get_what_neovide_was_until_i/')
        #self.fetch('https://www.reddit.com/r/neovim/comments/1i44spr/neovide_messed_up_my_brain_seriously/')
        self.fetch('https://www.google.com/search?q=amazon', return_content = False)
        self.fetch('https://www.amazon.com/Acqua-Natural-Spring-Plastic-Bottles/dp/B0067DVZEE', return_content = False)

    def initialize_driver(self):
        if self.driver is not None:
            return
        
        print("Initializing Chrome driver...")
        options = webdriver.ChromeOptions()
        
        if self.is_headless:
            options.add_argument("--headless=new")
        
        # Essential Chrome options for scraping
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Speed up loading
        options.add_argument("--disable-javascript")  # We don't need JS for basic scraping
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set Chrome binary location for macOS
        if sys.platform == 'darwin':  # macOS
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium"
            ]
            for path in chrome_paths:
                if os.path.exists(path):
                    options.binary_location = path
                    print(f"Using Chrome at: {path}")
                    break
        elif sys.platform.startswith('linux'):
            options.binary_location = "/snap/bin/chromium"

        # Set user agent
        ua = UserAgent()
        options.add_argument(f'user-agent={ua.random}')

        try:
            # Try ChromeDriverManager with explicit version handling
            print("Attempting to install/use ChromeDriver...")
            driver_path = ChromeDriverManager().install()
            print(f"ChromeDriver path: {driver_path}")
            
            # Check if the driver path is valid
            if os.path.exists(driver_path) and os.access(driver_path, os.X_OK):
                self.driver = webdriver.Chrome(
                    service=Service(driver_path),
                    options=options
                )
                print("✅ ChromeDriver initialized successfully")
            else:
                raise Exception(f"ChromeDriver not executable at {driver_path}")
                
        except Exception as e:
            print(f"❌ ChromeDriverManager failed: {e}")
            print("Trying system ChromeDriver...")
            
            # Fallback to system chromedriver
            try:
                self.driver = webdriver.Chrome(options=options)
                print("✅ System ChromeDriver initialized successfully")
            except Exception as e2:
                print(f"❌ System ChromeDriver failed: {e2}")
                raise Exception(f"Could not initialize Chrome driver. Please install ChromeDriver manually.")
        
        self.resize_randomly()

        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def fetch(self, url, verbose=True, return_content=True, request_intercept=True):
        self.initialize_driver()

        if verbose:
            print(f"Fetching {url}")

        if request_intercept:
            def intercept_request(request):
                blocked_domains = ['m.media-amazon.com', 'images-na.ssl-images-amazon.com']
                if any(domain in request.url for domain in blocked_domains):
                    request.abort()
            self.driver.request_interceptor = intercept_request

        try:
            self.driver.get(url)
            self.fetch_count += 1

            # Simulate human-like behavior
            scroll_amount = random.randint(300, 700)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_amount});")
            if self.fetch_count % 50 == 0:
                self.resize_randomly()
            #time.sleep(random.uniform(1, 3))

            return self.driver.page_source if return_content else True
        except Exception as e:
            print(f'  [bold red]Error occurred: {e}[/]')
            if isinstance(e, WebDriverException):
                print(f'  [blue]SeleniumFetcher restarting driver...[/]')
                self.quit()
                self.initialize_driver()
            return False

    def resize_randomly(self):
        self.driver.set_window_size(random.randint(1000, 1200), random.randint(600, 800))

    def run_javascript(self, script):
        return self.driver.execute_script(script)

    def quit(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

selenium_fetcher = None
def fetch_with_selenium(url, verbose=True):
    global selenium_fetcher
    if selenium_fetcher is None:
        print('[italic blue]Initializing Selenium...[/]')
        selenium_fetcher = SeleniumFetcher(isHeadless = False)
    return selenium_fetcher.fetch(url, verbose)

def run_javascript_selenium(script):
    global selenium_fetcher
    assert selenium_fetcher is not None
    return selenium_fetcher.run_javascript(script)

def quit_selenium():
    global selenium_fetcher
    assert selenium_fetcher is not None
    print('[italic blue]Quitting Selenium...[/]')
    selenium_fetcher.quit()

def extract_document_text(selenium_fetcher):
    # Replace multiple spaces with a single space and add line breaks after
    # paragraphs
    return selenium_fetcher.run_javascript(
        r'''
        return document.body.innerText.replace(/\s+/g, ' ').replace(/([.!?])\s+/g, '$1\n\n')
        '''
    )

def main():
    selenium_fetcher = SeleniumFetcher(is_headless = True)
    url = "https://www.amazon.com/AmazonBasics-Pre-sharpened-Wood-Cased-Pencils/dp/B071JM699P"
    html = selenium_fetcher.fetch(url, return_content = True)
    print("================================================================================")
    print(extract_document_text(selenium_fetcher))
    print("================================================================================")
    selenium_fetcher.quit()

if __name__ == "__main__":
    main()