import os
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

es = Elasticsearch(
    os.getenv("ELASTICSEARCH_URL"),
    basic_auth=(
        os.getenv("ELASTICSEARCH_USER"),
        os.getenv("ELASTICSEARCH_PASSWORD")
    ),
    verify_certs=False
)

INDEX_NAME = "flipkart_products"

def hybrid_search(query, k=5):
    query_vector = model.encode(query).tolist()

    response = es.search(
        index=INDEX_NAME,
        size=k,
        query={
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["name^3", "brand", "category", "sub_category"]
                        }
                    }
                ]
            }
        },
        knn={
            "field": "embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": 50
        }
    )

    return response["hits"]["hits"]


results = hybrid_search("wireless noise cancelling headphones")

for r in results:
    print(
        r["_source"]["name"],
        "| Brand:", r["_source"]["brand"],
        "| Price:", r["_source"]["discounted_price"]
    )
