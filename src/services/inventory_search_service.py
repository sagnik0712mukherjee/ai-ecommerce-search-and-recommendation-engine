from src.services.caching_service.get_cache import get_cached_results
from src.services.elastic_query_service import search_query
from src.services.queue_service import rerank_queue, rerank_in_progress, rerank_lock
import queue as py_queue
from config import config

def search_inventory(query, _from, size, model, INDEX_NAME, es, _type = config.search_type):
    
    normalized_query = query.strip().lower()
    
    # First try to fetch from cached results
    cached_response = get_cached_results(normalized_query, _type, es)
    if "hits" in cached_response and "hits" in cached_response["hits"] and len(cached_response["hits"]["hits"]):

        return cached_response["hits"]["hits"]

    # If not found in cache, proceed to generate vector and search
    query_vector = model.encode(normalized_query).tolist()

    # get search intent
    search_intent_body = search_query(query_vector, 0, 5, ["category", "sub_category", "sub_sub_category","sub_sub_sub_category"])
    search_intent_response = es.search(
        index=INDEX_NAME,
        body=search_intent_body
    )
    res = search_intent_response["hits"]["hits"]

    all_cats = [x["_source"].get("category", None) for x in res]
    all_sub_cats = [x["_source"].get("sub_category", None) for x in res]
    all_sub_sub_cats = [x["_source"].get("sub_sub_category", None) for x in res]
    all_sub_sub_sub_cats = [x["_source"].get("sub_sub_sub_category", None) for x in res]
    
    def most_frequent_val(values: list[str]) -> str:
        """
        Find the most frequently occurring value in a list.
        
        Args:
            values: List of string values.

        Returns:
            str: Most frequent value, or empty string if list is empty.
        """
        values = [v for v in values if isinstance(v, str)]
        return max(set(values), key=values.count) if values else ''

    cat_pred = most_frequent_val(all_cats)
    sub_cat_pred = most_frequent_val(all_sub_cats)
    sub_sub_cat_pred = most_frequent_val(all_sub_sub_cats)
    sub_sub_sub_cat_pred = most_frequent_val(all_sub_sub_sub_cats)

    revised_query = f"Item *{normalized_query}* is of category hierarchy {cat_pred} and {sub_cat_pred} and {sub_sub_cat_pred} and {sub_sub_sub_cat_pred}"
    revised_query_vector = model.encode(revised_query).tolist()

    body = search_query(revised_query_vector, _from, size + 30, _source={"excludes": ["embedding"]}, cat_pred=cat_pred, sub_cat_pred=sub_cat_pred, sub_sub_cat_pred=sub_sub_cat_pred, sub_sub_sub_cat_pred=sub_sub_sub_cat_pred)

    response = es.search(
        index=INDEX_NAME,
        body=body
    )

    # Fire-and-forget async reranking in queue
    result_for_reranking = [item["_source"] for item in response["hits"]["hits"]]
    # 🔑 Enqueue ONLY if not already in progress
    with rerank_lock:
        key = (normalized_query, _type)
        if key not in rerank_in_progress:
            rerank_in_progress.add(key)
            try:
                rerank_queue.put_nowait(
                    (normalized_query, result_for_reranking, _type, es)
                )
            except py_queue.Full:
                # rollback if enqueue fails
                rerank_in_progress.discard(key)

    return response["hits"]["hits"][:size]

