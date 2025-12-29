from config import config
from src.services.elastic_query_service import get_cache_query, get_items_by_id_query

CACHE_INDEX = config.CACHE_INDEX
INVENTORY_INDEX = config.INVENTORY_INDEX

def get_cached_results(query, _type, es):

    sorted_hits = []

    query_to_get_cache = get_cache_query(query, _type)
    response = es.search(
        index=CACHE_INDEX,
        body=query_to_get_cache
    )

    if response["hits"]["total"]["value"] > 0:
        cached_product_ids = response["hits"]["hits"][0]["_source"]["cached_product_ids"]

        query_to_get_items = get_items_by_id_query(cached_product_ids)
        items_response = es.search(
            index=INVENTORY_INDEX,
            body=query_to_get_items
        )

        hits = items_response["hits"]["hits"]
        if hits:

            # 🔑 Map product_id → ES hit
            hit_map = {
                hit["_source"]["product_id"]: hit
                for hit in hits
            }

            # 🔑 Reorder hits exactly as LLM reranked IDs
            sorted_hits = [
                hit_map[pid]
                for pid in cached_product_ids
                if pid in hit_map
            ]

    # Placeholder for actual caching logic
    return {
        "hits": {
            "hits": sorted_hits
        }
    }