import json
import scrapy

class GetCategorySpider(scrapy.Spider):
    name = "get_categories"

    async def start(self):
        urls = [
            "https://fr.trustpilot.com/categories",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_categories)

    def parse_categories(self, response: scrapy.http.Response):
        """Parse the categories page and extract all category information"""

        # Find categories div container
        categories_div = response.xpath('//div[starts-with(@class, "categories")]')

        if not categories_div:
            self.logger.error("Could not find categories desktop container")
            return None

        # Check if categories_desktop selector returns multiple elements
        if len(categories_div) > 1:
            self.logger.error("Found multiple categories desktop containers - expected only one")
            return None

        # Find all category links that start with /categories/
        category_links = categories_div.xpath('//a[starts-with(@href, "/categories/")]')
        
        if not category_links:
            self.logger.error("Could not find any category links")
            return None

        # Extract href and text from category links into JSON structure
        categories_json = []

        for link in category_links:
            href = link.attrib.get('href')
            name = link.css('::text').get()
            if href and name:
                # Extract slug from href by removing /categories/ prefix
                slug = href.replace('/categories/', '')
                categories_json.append({
                    'link': href,
                    'name': name.strip(),
                    'slug': slug
                })
        # Save categories_json to file
        with open('category_links.json', 'w', encoding='utf-8') as f:
            json.dump(categories_json, f, ensure_ascii=False, indent=2)
