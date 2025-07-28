import json
import scrapy

class GetProductsSpider(scrapy.Spider):
    name = "get_products"

    async def start(self):
        """Parse the category page and extract all product information"""

        # Load products from JSON file
        try:
            with open('products.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            base_url = "https://fr.trustpilot.com"
            
            for product in products:
                product_url = base_url + product['product_link']
                yield scrapy.Request(
                    url=product_url, 
                    callback=self.get_reviews,
                    cb_kwargs={
                        'category_slug': product['category_slug'],
                        'category_name': product['category_name'], 
                        'product_slug': product['product_slug']
                    }
                )

        except FileNotFoundError:
            self.logger.error("Could not find categories.json file")
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON in categories.json file") 


    def get_products(self, response: scrapy.http.Response, category_name: str, category_slug: str) -> scrapy.Request | None:
        """Parse the category page and extract all company information"""
                # Find categories div container

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
                products_json.append({
                    'product_link': href,
                    'product_slug': product_slug,
                    'category_slug': category_slug,
                    'category_name': category_name
                })

        # Initialize json_content
        json_content = []
        
        # Try to read existing products.json file
        try:
            with open('products.json', 'r', encoding='utf-8') as f:
                json_content = json.load(f)
        except FileNotFoundError:
            # File doesn't exist yet, will be created when writing
            pass
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON in products.json file")

        new_content = json_content + products_json

        with open(f'products.json', 'w', encoding='utf-8') as f:
            json.dump(new_content, f, ensure_ascii=False, indent=2)
