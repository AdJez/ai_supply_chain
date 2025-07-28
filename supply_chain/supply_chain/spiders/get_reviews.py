import json
import scrapy

class GetReviewsSpider(scrapy.Spider):
    name = "get_reviews"

    async def start(self):
        """Parse the categories page and extract all category information"""

        # Load categories from JSON file
        try:
            with open('products.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            base_url = "https://fr.trustpilot.com"
            
            for product in products:
                product_url = base_url + product['product_link']
                yield scrapy.Request(url=product_url, callback=self.get_reviews, cb_kwargs={'category_slug': product['category_slug'], 'category_name': product['category_name'], 'product_slug': product['product_slug']})

        except FileNotFoundError:
            self.logger.error("Could not find products.json file")
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON in products.json file") 


    def get_reviews(self, response, category_name, category_slug, product_slug):
        """Parse the product page and extract all review information"""
        # Find reviews div container

        reviews_div = response.xpath('//section[starts-with(@class, "styles_reviewListContainer")]')
        if not reviews_div:
            self.logger.error("Could not find reviews div container")

        # Check if reviews_div selector returns multiple elements
        if len(reviews_div) > 1:
            self.logger.error("Found multiple reviews containers - expected only one")

        # Reviews
        reviews = reviews_div.xpath('//article[starts-with(@class, "styles_reviewCard")]')

        if not reviews:
            self.logger.error("Could not find reviews div")

        reviews_json = []
        for review in reviews:
            # Get review header div
            review_header = review.xpath('//div[starts-with(@class, "styles_reviewCardInnerHeader")]')
            if not review_header:
                self.logger.error("Could not find review header div")
            
            # Extract datetime from time tag
            review_datetime = review_header.xpath('.//time/@datetime').get()
            if not review_datetime:
                self.logger.error("Could not find review datetime")

            review_header = review.xpath('//div[starts-with(@class, "styles_reviewHeader")]')
            if not review_header:
                self.logger.error("Could not find review rating header div")
            # Extract service rating from data attribute
            service_rating = review_header.xpath('./@data-service-review-rating').get()
            if not service_rating:
                self.logger.error("Could not find service rating")

            review_content = review.xpath('//div[starts-with(@class, "styles_reviewContent")]')
            if not review_content:
                self.logger.error("Could not find review content div")

            # Extract review title from h2 tag
            review_title = review_content.xpath('.//h2/text()').get()
            if not review_title:
                self.logger.error("Could not find review title")

            # Extract review text from first p tag
            review_text = review_content.xpath('.//p/text()').getall()
            if not review_text:
                self.logger.error("Could not find review text")

            # Create review JSON with datetime
            review_json = {
                'datetime': review_datetime,
                'service_rating': service_rating,
                'title': review_title,
                'text': review_text,
                'category_slug': category_slug,
                'category_name': category_name,
                'product_slug': product_slug
            }
            reviews_json.append(review_json)

        if not reviews_div:
            self.logger.error("Could not find any reviews")

        # Initialize json_content
        json_content = []
        
        # Try to read existing products.json file
        try:
            with open('reviews.json', 'r', encoding='utf-8') as f:
                json_content = json.load(f)
        except FileNotFoundError:
            # File doesn't exist yet, will be created when writing
            pass
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON in reviews.json file")

        new_content = json_content + reviews_json

        with open(f'reviews.json', 'w', encoding='utf-8') as f:
            json.dump(new_content, f, ensure_ascii=False, indent=2)
