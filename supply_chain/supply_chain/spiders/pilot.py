import json
from scrapy.selector import Selector
import pandas as pd
import scrapy

class TrustSpider(scrapy.Spider):
    name = "trust"

    async def start(self):
        urls = [
            "https://fr.trustpilot.com/review/www.ma-cl%C3%A9.fr",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def get_reviews_from_response(self, response):
        try:
            reviews_raw = response.css('[id="__NEXT_DATA__"]::text').extract_first()
            reviews_raw = json.loads(reviews_raw)

            return reviews_raw["props"]["pageProps"]["reviews"]

        except (json.JSONDecodeError, AttributeError) as e:
            return []

    def parse(self, response):
        reviews_data = []
        reviews = self.get_reviews_from_response(response)

        for review in reviews:
            data = {
                'Date': pd.to_datetime(review["dates"]["publishedDate"]).strftime("%Y-%m-%d"),
                'Author': review["consumer"]["displayName"],
                'Body': review["text"],
                'Heading': review["title"],
                'Rating': review["rating"],
                'Location': review["consumer"]["countryCode"]
            }
            reviews_data.append(data)

        # Remove duplicates based on the 'Body' field
        reviews_data = [dict(t) for t in {tuple(d.items()) for d in reviews_data}]

        return reviews_data



