from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from collections import Counter

import threading
import time
import pandas as pd
import numpy as np
import re
import concurrent.futures
import matplotlib.pyplot as plt
import seaborn as sns
import math

class WebScraper:
    def __init__(self):
        self.setup_chrome_options()
        self.setup_driver()

    def setup_chrome_options(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Additional recommended options
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--disable-extensions')

    def setup_driver(self):
        try:
            # Using ChromeDriver from system PATH
            service = Service('chromedriver')  # Make sure chromedriver is in your PATH
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            self.wait = WebDriverWait(self.driver, 10)  # 10 seconds timeout
        except Exception as e:
            print(f"Error setting up driver: {e}")
            self.driver = None

    def scrape_website(self, url):
        if not self.driver:
            print("Driver not initialized")
            return None

        try:
            self.driver.get(url)
            print(f"Successfully loaded: {url}")
            print(f"Page title: {self.driver.title}")

            # Get page source and create BeautifulSoup object
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            return soup

        except Exception as e:
            print(f"Error scraping website: {e}")
            return None

    def close(self):
        if self.driver:
            self.driver.quit()

def main():
    # Create scraper instance
    scraper = WebScraper()
    
    try:
        # Example usage
        soup = scraper.scrape_website("https://www.google.com")
        
        if soup:
            # Example data processing
            print("\nProcessing data...")
            
            # Create a sample DataFrame
            data = {
                'Column1': np.random.rand(5),
                'Column2': np.random.rand(5)
            }
            df = pd.DataFrame(data)
            print("\nSample DataFrame:")
            print(df)

            # Create a sample plot
            plt.figure(figsize=(10, 6))
            sns.scatterplot(data=df, x='Column1', y='Column2')
            plt.title('Sample Plot')
            plt.show()

    finally:
        # Always close the driver
        scraper.close()

if __name__ == "__main__":
    main()
