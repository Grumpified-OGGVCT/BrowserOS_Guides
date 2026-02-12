#!/usr/bin/env python3
"""
Generate screenshots of the static website for README documentation
"""
import os
import sys
import time
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_chrome_paths():
    """Get Chrome/Chromium binary and chromedriver paths based on platform and environment"""
    system = platform.system()
    
    # Check environment variables first
    chrome_binary = os.environ.get('CHROME_BINARY')
    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
    
    if chrome_binary and chromedriver_path:
        return chrome_binary, chromedriver_path
    
    # Platform-specific defaults
    if system == 'Linux':
        chrome_binary = chrome_binary or '/usr/bin/chromium'
        chromedriver_path = chromedriver_path or '/usr/bin/chromedriver'
    elif system == 'Darwin':  # macOS
        chrome_binary = chrome_binary or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        chromedriver_path = chromedriver_path or '/usr/local/bin/chromedriver'
    elif system == 'Windows':
        chrome_binary = chrome_binary or 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        chromedriver_path = chromedriver_path or 'C:\\chromedriver.exe'
    else:
        raise RuntimeError(f"Unsupported platform: {system}")
    
    return chrome_binary, chromedriver_path

def setup_driver():
    """Setup Chrome driver with headless options"""
    chrome_binary, chromedriver_path = get_chrome_paths()
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Only set binary location if the file exists
    if os.path.exists(chrome_binary):
        chrome_options.binary_location = chrome_binary
    else:
        print(f"Warning: Chrome binary not found at {chrome_binary}, using system default")
    
    # Create service with chromedriver path if it exists
    if os.path.exists(chromedriver_path):
        service = Service(chromedriver_path)
    else:
        print(f"Warning: Chromedriver not found at {chromedriver_path}, using system PATH")
        service = Service()  # Will use chromedriver from PATH
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error: Failed to initialize Chrome driver: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Chrome/Chromium is installed")
        print("2. Ensure chromedriver is installed and in PATH")
        print("3. Set CHROME_BINARY and CHROMEDRIVER_PATH environment variables if needed")
        sys.exit(1)

def take_screenshot(driver, url, output_path, wait_selector=None, wait_time=2):
    """Take a screenshot of a webpage"""
    print(f"Navigating to: {url}")
    driver.get(url)
    
    if wait_selector:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
            )
        except Exception as e:
            print(f"Warning: Could not find selector {wait_selector}: {e}")
    
    time.sleep(wait_time)
    
    print(f"Saving screenshot to: {output_path}")
    driver.save_screenshot(output_path)
    print(f"Screenshot saved successfully")

def main():
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    docs_dir = os.path.join(repo_root, 'docs')
    screenshots_dir = os.path.join(docs_dir, 'screenshots')
    
    # Create screenshots directory if it doesn't exist
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # Setup driver
    print("Setting up Chrome driver...")
    driver = setup_driver()
    
    try:
        # Base URL for local files
        base_url = f'file://{docs_dir}'
        
        # Screenshot 1: Hero section (main page)
        print("\n1. Capturing hero section...")
        take_screenshot(
            driver,
            f'{base_url}/index.html',
            os.path.join(screenshots_dir, '01-hero-section.png'),
            wait_selector='.hero-title',
            wait_time=3
        )
        
        # Screenshot 2: Workflows section
        print("\n2. Capturing workflows section...")
        driver.get(f'{base_url}/index.html#workflows')
        time.sleep(2)
        take_screenshot(
            driver,
            f'{base_url}/index.html#workflows',
            os.path.join(screenshots_dir, '02-workflows-section.png'),
            wait_time=2
        )
        
        # Screenshot 3: Use cases section
        print("\n3. Capturing use cases section...")
        driver.get(f'{base_url}/index.html#use-cases')
        time.sleep(2)
        take_screenshot(
            driver,
            f'{base_url}/index.html#use-cases',
            os.path.join(screenshots_dir, '03-use-cases-section.png'),
            wait_time=2
        )
        
        # Screenshot 4: MCP/Agentic section
        print("\n4. Capturing MCP/Agentic section...")
        driver.get(f'{base_url}/index.html#mcp-agentic')
        time.sleep(2)
        take_screenshot(
            driver,
            f'{base_url}/index.html#mcp-agentic',
            os.path.join(screenshots_dir, '04-mcp-agentic-section.png'),
            wait_time=2
        )
        
        # Screenshot 5: Repo browser
        print("\n5. Capturing repo browser...")
        take_screenshot(
            driver,
            f'{base_url}/repo-browser.html',
            os.path.join(screenshots_dir, '05-repo-browser.png'),
            wait_selector='.file-tree',
            wait_time=3
        )
        
        # Screenshot 6: Search functionality
        print("\n6. Capturing search section...")
        driver.get(f'{base_url}/index.html#search')
        time.sleep(2)
        take_screenshot(
            driver,
            f'{base_url}/index.html#search',
            os.path.join(screenshots_dir, '06-search-section.png'),
            wait_time=2
        )
        
        print("\n✅ All screenshots generated successfully!")
        print(f"Screenshots saved to: {screenshots_dir}")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
