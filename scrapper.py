import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JumiaScraperMA:
    
    def __init__(self):
        self.base_url = "https://www.jumia.ma"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.products_data = []
        self.categories = {}
        
    def get_categories(self):
        try:
            logger.info("Fetching categories from homepage...")
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get main categories from the navigation bar (class='itm')
            category_links = soup.find_all('a', class_='itm', attrs={'role': 'menuitem'})
            
            logger.info(f"Found {len(category_links)} main categories")
            
            for link in category_links:
                href = link.get('href')
                span = link.find('span', class_='text')
                if span and href:
                    category_name = span.get_text(strip=True)
                    category_url = urljoin(self.base_url, href)
                    self.categories[category_name] = category_url
                    logger.info(f"Main category found: {category_name} -> {category_url}")
            
            # Get hidden categories from the submenu (class='tit' inside div class='sub')
            # These are the categories in the dropdown menu
            submenu_categories = soup.find_all('a', class_='tit', attrs={'role': 'menuitem'})
            
            logger.info(f"Found {len(submenu_categories)} submenu categories")
            
            for link in submenu_categories:
                href = link.get('href')
                if href:
                    category_name = link.get_text(strip=True)
                    category_url = urljoin(self.base_url, href)
                    # Avoid duplicates
                    if category_name not in self.categories:
                        self.categories[category_name] = category_url
                        logger.info(f"Submenu category found: {category_name} -> {category_url}")
            
            return self.categories
            
        except requests.RequestException as e:
            logger.error(f"Error fetching categories: {e}")
            return {}
    
    def scrape_category_products(self, category_name, category_url, max_pages=5):
        try:
            logger.info(f"Scraping category: {category_name}")
            page = 1
            
            while page <= max_pages:
                try:
                    page_url = f"{category_url}?page={page}"
                    logger.info(f"Scraping page {page}: {page_url}")
                    
                    response = requests.get(page_url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    products = soup.find_all('article', class_='prd')
                    
                    if not products:
                        logger.info(f"No more products found on page {page}")
                        break
                    
                    logger.info(f"Found {len(products)} products on page {page}")
                    
                    for product in products:
                        product_data = self.extract_product_info(product, category_name)
                        if product_data:
                            self.products_data.append(product_data)
                    
                    page += 1
                    time.sleep(2)
                    
                except requests.RequestException as e:
                    logger.warning(f"Error scraping page {page}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error in scrape_category_products: {e}")
    
    def extract_product_info(self, product_element, category_name):
        try:
            product_info = {'category': category_name}
            
            name_elem = product_element.find('h3', class_='name')
            if name_elem:
                product_info['name'] = name_elem.get_text(strip=True)
            
            price_elem = product_element.find('div', class_='prc')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                product_info['price'] = price_text
            
            rating_elem = product_element.find('div', class_='rating')
            if rating_elem:
                product_info['rating'] = rating_elem.get_text(strip=True)
            
            link_elem = product_element.find('a', class_='core')
            if link_elem and link_elem.get('href'):
                product_info['url'] = urljoin(self.base_url, link_elem['href'])
            
            
            return product_info if product_info else None
            
        except Exception as e:
            logger.error(f"Error extracting product info: {e}")
            return None
    
    def scrape_all_categories(self, max_pages_per_category=5):
        try:
            categories = self.get_categories()
            
            if not categories:
                logger.error("No categories found!")
                return
            
            logger.info(f"Starting to scrape {len(categories)} categories...")
            
            for category_name, category_url in categories.items():
                self.scrape_category_products(category_name, category_url, max_pages_per_category)
                time.sleep(3)
            
            logger.info(f"Scraping complete! Total products scraped: {len(self.products_data)}")
            
        except Exception as e:
            logger.error(f"Error in scrape_all_categories: {e}")
    
    def save_to_csv(self, filename='jumia_products.csv'):
        try:
            if not self.products_data:
                logger.warning("No products to save!")
                return
            
            df = pd.DataFrame(self.products_data)
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Data saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
    

            
    
    def get_statistics(self):
        if not self.products_data:
            logger.info("No data to display statistics!")
            return
        
        df = pd.DataFrame(self.products_data)
        
        print("\n" + "="*50)
        print("SCRAPING STATISTICS")
        print("="*50)
        print(f"Total products scraped: {len(self.products_data)}")
        print(f"\nProducts per category:")
        print(df['category'].value_counts())
        print("\n" + "="*50 + "\n")


def main():
    
    scraper = JumiaScraperMA()
    

    scraper.scrape_all_categories(max_pages_per_category=50)
    
    scraper.save_to_csv('jumia_products.csv')    
    scraper.get_statistics()


if __name__ == "__main__":
    main()
