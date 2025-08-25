import json
from time import sleep
from urllib.parse import urlparse, parse_qs

import scrapy

class GetProductsSpider(scrapy.Spider):
    name = "get_products"

    async def start(self):
        """Parse the category page and extract all product information"""

        # Load products from JSON file
        try:
            with open('category_links.json', 'r', encoding='utf-8') as f:
                categories = json.load(f)
            base_url = "https://fr.trustpilot.com"


            for category in categories:
                category_url = base_url + category['link']

                yield scrapy.Request(
                    url=category_url,
                    callback=self.get_products,
                    cb_kwargs={
                        'category_slug': category['slug'],
                        'category_name': category['name'],
                    }
                )

        except FileNotFoundError:
            self.logger.error("Could not find category links json file")
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON in categories.json file") 


    def get_products(self, response: scrapy.http.Response, category_name: str, category_slug: str):
        """Parse the category page and extract all company information"""
                # Find categories div container
        sleep(1)

        products_div = response.xpath('//div[starts-with(@class, "categorylayout_leftSection")]')
        if not products_div:
            self.logger.error("Could not find products div container")

        # Check if categories_desktop selector returns multiple elements
        if len(products_div) > 1:
            self.logger.error("Found multiple products containers - expected only one")

        # Find all category links that start with /review/
        products_links = products_div.xpath('//a[starts-with(@href, "/review/")]')

        if not products_links:
            self.logger.error("Could not find any product links")

        # Extract product links and create JSON structure
        products_json = []
        
        for link in products_links:
            href = link.attrib.get('href')
            product_slug = href.split('/')[-1]
            if href and product_slug:
                if product_slug in products_json:
                    self.logger.info("Product %s already in products json, operation skipped", product_slug)
                    continue
                products_json.append({
                    product_slug : {
                        'product_link': href,
                        'category_slug': category_slug,
                        'category_name': category_name
                    }
                })

        # Initialize json_content
        json_content = []
        
        # Try to read existing product links json file
        try:
            with open('product_links.json', 'r', encoding='utf-8') as f:
                json_content = json.load(f)
        except FileNotFoundError:
            # File doesn't exist yet, will be created when writing
            pass
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON in products.json file")

        new_content = json_content + products_json

        with open(f'product_links.json', 'w', encoding='utf-8') as f:
            json.dump(new_content, f, ensure_ascii=False, indent=2)

        # Pagination: look for the next page button; only follow if not disabled
        next_button = response.xpath('//a[@name="pagination-button-next"]')

        if next_button.get():
            aria_disabled = (next_button.xpath('@aria-disabled').get() or '').lower()
            next_href = next_button.xpath('@href').get()
            is_disabled = (aria_disabled == 'true') or (not next_href)

            if is_disabled:
                self.logger.info("Next pagination button is disabled; stopping pagination for this category: %s", category_slug)
                return

            next_url = response.urljoin(next_href)

            self.logger.info("Next pagination button found, following the link: %s", next_url)

            yield scrapy.Request(
                url=next_url,
                callback=self.get_products,
                cb_kwargs={
                    'category_slug': category_slug,
                    'category_name': category_name,
                }
            )
