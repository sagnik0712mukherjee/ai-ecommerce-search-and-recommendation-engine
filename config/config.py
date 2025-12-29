import os

ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")
ELASTICSEARCH_USER = os.environ.get("ELASTICSEARCH_USER")
ELASTICSEARCH_PASSWORD = os.environ.get("ELASTICSEARCH_PASSWORD")

CACHE_INDEX = "cached_search_results"
INVENTORY_INDEX = "flipkart_products"

recommendation_type = "recommendations"
search_type = "search"

print(ELASTICSEARCH_PASSWORD)