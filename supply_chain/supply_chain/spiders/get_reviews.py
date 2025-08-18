import json
import csv
import os
import scrapy

class GetReviewsSpider(scrapy.Spider):
    name = "get_reviews"

    async def start(self):
        """Parse the products page and extract all review information"""

        # Load products from JSON file
        try:
            with open('product_links.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            base_url = "https://fr.trustpilot.com"
            
            for product in products:
                # Extract the first (and only) key from the product dict
                try:
                    slug = next(iter(product))
                except StopIteration:
                    self.logger.error("Encountered empty product object; skipping")
                    continue

                product_url = base_url + product[slug]['product_link']
                yield scrapy.Request(
                    url=product_url,
                    callback=self.get_reviews,
                    cb_kwargs={
                        'category_slug': product[slug]['category_slug'],
                        'category_name': product[slug]['category_name'],
                        'product_slug': slug
                    }
                )

        except FileNotFoundError:
            self.logger.error("Could not find products.json file")
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON in products.json file") 


    def get_reviews(self, response: scrapy.http.Response, category_name: str, category_slug: str, product_slug: str):
        """Parse the product page and extract all review information"""
        # Find reviews div container


        reviews_div = response.xpath('//section[starts-with(@class, "styles_reviewListContainer")]')
        if not reviews_div:
            self.logger.error("Could not find reviews div container")

        # Check if reviews_div selector returns multiple elements
        if len(reviews_div) > 1:
            self.logger.error("Found multiple reviews containers - expected only one")

        # Reviews
        reviews = reviews_div[0].xpath('.//article')

        if not reviews:
            self.logger.error("Could not find reviews div for product %s", product_slug)

        reviews_json = []
        for review in reviews:
            # Get review header div
            review_header = review.xpath('.//div[starts-with(@class, "styles_reviewCardInnerHeader")]')
            if not review_header:
                self.logger.error("Could not find review header div")
            
            # Extract datetime from time tag
            review_datetime = review_header.xpath('.//time/@datetime').get()
            if not review_datetime:
                self.logger.error("Could not find review datetime")

            review_header = review.xpath('.//div[starts-with(@class, "styles_reviewHeader")]')
            if not review_header:
                self.logger.error("Could not find review rating header div")
            # Extract service rating from data attribute
            service_rating = review_header.xpath('./@data-service-review-rating').get()
            if not service_rating:
                self.logger.error("Could not find service rating")

            review_content = review.xpath('.//div[starts-with(@class, "styles_reviewContent")]')
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

        # Also write/append to CSV
        if reviews_json:
            csv_filename = 'reviews.csv'
            # Determine field order from the keys of the first review
            fieldnames = list(reviews_json[0].keys())

            # Ensure the CSV file exists and check if it's empty to decide header writing
            file_exists = os.path.exists(csv_filename)
            file_empty = (not file_exists) or (os.path.getsize(csv_filename) == 0)

            # Prepare rows (convert list fields like 'text' to a single string)
            prepared_rows = []
            for r in reviews_json:
                row = dict(r)
                # Convert list of paragraphs to a single string
                if isinstance(row.get('text'), list):
                    row['text'] = ' '.join([t.strip() for t in row['text'] if t is not None]).strip()
                prepared_rows.append(row)

            # Append rows to CSV and write header if needed
            with open(csv_filename, 'a', encoding='utf-8', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if file_empty:
                    writer.writeheader()
                for row in prepared_rows:
                    writer.writerow(row)

            # Pagination: look for the next page button; only follow if not disabled

        next_button = response.xpath('//a[@name="pagination-button-next"]')

        if next_button:
            aria_disabled = (next_button.xpath('@aria-disabled').get() or '').lower()
            next_href = next_button.xpath('@href').get()
            is_disabled = (aria_disabled == 'true') or (not next_href)

            if is_disabled:
                self.logger.info("Next pagination button is disabled; stopping pagination for this category: %s",
                                 category_slug)
                return

            next_url = response.urljoin(next_href)

            self.logger.info("Next pagination button found, following the link: %s", next_url)

            yield scrapy.Request(
                url=next_url,
                callback=self.get_reviews,
                cb_kwargs={
                    'product_slug': product_slug,
                    'category_slug': category_slug,
                    'category_name': category_name,
                }
            )
