import json
import random
import time
from dataclasses import dataclass, asdict
from typing import List
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

@dataclass
class ProductData:
    name: str = "None"
    price: str = "None"
    rating: str = "None"
    sold: str = "None"
    location: str = "None"

class LazadaScraper:
    def __init__(self):
        self.base_url = 'https://www.lazada.sg/catalog/?q='
        self.keywords = ['gaming monitor']
        self.data: List[ProductData] = []
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]

    def setup_driver(self):
        options = Options()
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-notifications')
        # Remove headless mode for debugging
        # options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        selected_agent = random.choice(self.user_agents)
        options.add_argument(f'user-agent={selected_agent}')

        seleniumwire_options = {
            'verify_ssl': False,
            'suppress_connection_errors': False
        }

        driver = webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": selected_agent})
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        driver.set_page_load_timeout(30)
        return driver

    def wait_for_element(self, driver, selector, timeout=10):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except TimeoutException:
            print(f"Timeout waiting for element: {selector}")
            return None

    def extract_product_data(self, driver) -> List[ProductData]:
        products = []
        print("Waiting for products to load...")
        try:
            # Wait for the product grid to load
            main_container = self.wait_for_element(driver, '.Bm3ON')
            if not main_container:
                print("Could not find main container")
                return products

            print("Products found, starting extraction...")
            items = driver.find_elements(By.CSS_SELECTOR, '.Bm3ON')
            print(f"Found {len(items)} items")
            
            for index, item in enumerate(items[:30]):
                try:
                    print(f"\nExtracting details for product {index + 1}:")
                    
                    name = item.find_element(By.CSS_SELECTOR, '.RfADt').text.strip()
                    price = item.find_element(By.CSS_SELECTOR, '.aBrP0').text.strip()
                    rating = "N/A"
                    try:
                        rating_element = item.find_element(By.CSS_SELECTOR, '.qzqFw')
                        if rating_element:
                            rating_text = rating_element.text.strip()
                            if rating_text:
                                rating = rating_text.strip('()')
                    except Exception as e:
                        print(f"Rating extraction error: {str(e)}")

                    sold = "N/A"
                    try:
                        sold_element = item.find_element(By.CSS_SELECTOR, '._1cEkb span')
                        if sold_element:
                            sold_text = sold_element.text.strip()
                            if 'sold' in sold_text.lower():
                                sold = sold_text
                    except Exception as e:
                        print(f"Sold count extraction error: {str(e)}")
                    try:
                        location = item.find_element(By.CSS_SELECTOR, '.oa6ri').text.strip()
                    except:
                        location = "N/A"
                    print(f"Name: {name[:50]}...")
                    print(f"Price: {price}")
                    print(f"Rating: {rating}")
                    print(f"Sold: {sold}")
                    print(f"Location: {location}")
                    
                    product = ProductData(
                        name=name,
                        price=price,
                        rating=rating,
                        sold=sold,
                        location=location
                    )
                    products.append(product)
                    
                    time.sleep(random.uniform(0.2, 0.5))
                    
                except Exception as e:
                    print(f"\nError extracting product {index + 1}: {str(e)}")
                    continue

            print(f"Total products extracted: {len(products)}")
            return products

        except TimeoutException:
            print("Timeout waiting for products to load")
            print(f"Current URL: {driver.current_url}")
        except Exception as e:
            print(f"Error in product extraction: {str(e)}")

        return products


    def scrape_keyword(self, keyword: str, max_retries=3):
        driver = None
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"\nStarting scrape for keyword: {keyword} (Attempt {retry_count + 1}/{max_retries})")
                driver = self.setup_driver()
                url = f"{self.base_url}{keyword}"
                print(f"Navigating to URL: {url}")
                
                driver.get(url)
                time.sleep(random.uniform(10, 15))  
                
                products = self.extract_product_data(driver)
                if products:  
                    self.data.extend(products)
                    print(f"Added {len(products)} products to data")
                    break
                    
                retry_count += 1
                
            except Exception as e:
                print(f"Error during scraping attempt {retry_count + 1}: {str(e)}")
                retry_count += 1
                time.sleep(random.uniform(5, 10)) 
            finally:
                if driver:
                    driver.quit()

    def save_to_file(self, filename: str = 'lazada_products.json'):
        if not self.data:
            print("No data to save!")
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([asdict(product) for product in self.data], f, ensure_ascii=False, indent=2)
            print(f"Successfully saved {len(self.data)} products to {filename}")
        except Exception as e:
            print(f"Error saving to file: {str(e)}")

    def run(self):
        print("Starting scraper...")
        for keyword in self.keywords:
            self.scrape_keyword(keyword)
        self.save_to_file()
        print("Scraping completed!")

if __name__ == "__main__":
    scraper = LazadaScraper()
    scraper.run()
