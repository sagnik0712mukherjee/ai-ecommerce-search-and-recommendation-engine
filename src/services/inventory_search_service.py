from src.services.caching_service.get_cache import get_cached_results
from src.services.elastic_query_service import search_query
from src.services.queue_service import rerank_queue, rerank_in_progress, rerank_lock
import queue as py_queue
from config import config


def search_inventory(query, _from, size, model, INDEX_NAME, es, _type=config.search_type):
    """
    Orchestrates the end-to-end AI-powered search flow for the inventory.

    This function performs hybrid semantic retrieval using Elasticsearch by:
    1. Normalizing and cache-checking the incoming query
    2. Generating semantic embeddings for the query
    3. Inferring category intent via nearest-neighbor retrieval
    4. Rewriting the query in a RAG-style manner using inferred hierarchy
    5. Executing a hybrid vector + keyword search
    6. Triggering asynchronous re-ranking without impacting user latency

    Re-ranking is intentionally decoupled from the request path and executed
    asynchronously to allow relevance to improve over time while keeping
    search latency predictable.

    Args:
        query (str): Raw user search query.
        _from (int): Pagination offset.
        size (int): Number of results to return.
        model: SentenceTransformer-compatible embedding model.
        INDEX_NAME (str): Elasticsearch index name.
        es: Elasticsearch client instance.
        _type (str): Search type identifier used for caching and reranking.

    Returns:
        list: Top `size` search results ordered by relevance.
    """

    # Normalize query for cache consistency and embedding stability
    normalized_query = query.strip().lower()

    # Attempt cache lookup to avoid redundant vector computation and ES calls
    cached_response = get_cached_results(normalized_query, _type, es)
    if (
        isinstance(cached_response, dict)
        and "hits" in cached_response
        and "hits" in cached_response["hits"]
        and cached_response["hits"]["hits"]
    ):
        return cached_response["hits"]["hits"]

    # Generate embedding for the normalized query
    query_vector = model.encode(normalized_query).tolist()

    # Retrieve nearest neighbors to infer category intent
    search_intent_body = search_query(
        query_vector,
        0,
        5,
        ["category", "sub_category", "sub_sub_category", "sub_sub_sub_category"],
    )
    search_intent_response = es.search(index=INDEX_NAME, body=search_intent_body)
    intent_hits = search_intent_response["hits"]["hits"]

    # Extract hierarchical category signals from retrieved neighbors
    all_cats = [x["_source"].get("category") for x in intent_hits]
    all_sub_cats = [x["_source"].get("sub_category") for x in intent_hits]
    all_sub_sub_cats = [x["_source"].get("sub_sub_category") for x in intent_hits]
    all_sub_sub_sub_cats = [x["_source"].get("sub_sub_sub_category") for x in intent_hits]

    def most_frequent_val(values: list[str]) -> str:
        """
        Returns the most frequently occurring non-null string value in a list.

        Args:
            values (list[str]): List of candidate string values.

        Returns:
            str: Most frequent value, or empty string if none are valid.
        """
        valid_values = [v for v in values if isinstance(v, str)]
        return max(set(valid_values), key=valid_values.count) if valid_values else ""

    # Infer most likely category hierarchy using frequency consensus
    cat_pred = most_frequent_val(all_cats)
    sub_cat_pred = most_frequent_val(all_sub_cats)
    sub_sub_cat_pred = most_frequent_val(all_sub_sub_cats)
    sub_sub_sub_cat_pred = most_frequent_val(all_sub_sub_sub_cats)

    # Rewrite query with inferred hierarchy (RAG-style augmentation)
    revised_query = (
        f"Item *{normalized_query}* is of category hierarchy "
        f"{cat_pred} and {sub_cat_pred} and {sub_sub_cat_pred} and {sub_sub_sub_cat_pred}"
    )
    revised_query_vector = model.encode(revised_query).tolist()

    # Perform hybrid retrieval with semantic, lexical, and category signals
    body = search_query(
        revised_query_vector,
        _from,
        size + 30,
        _source={"excludes": ["embedding"]},
        cat_pred=cat_pred,
        sub_cat_pred=sub_cat_pred,
        sub_sub_cat_pred=sub_sub_cat_pred,
        sub_sub_sub_cat_pred=sub_sub_sub_cat_pred,
    )
    response = es.search(index=INDEX_NAME, body=body)

    # Trigger asynchronous re-ranking (fire-and-forget)
    result_for_reranking = [item["_source"] for item in response["hits"]["hits"]]
    with rerank_lock:
        key = (normalized_query, _type)
        if key not in rerank_in_progress:
            rerank_in_progress.add(key)
            try:
                rerank_queue.put_nowait((normalized_query, result_for_reranking, _type, es))
            except py_queue.Full:
                # Roll back state if enqueue fails
                rerank_in_progress.discard(key)

    # Return top-N results immediately without waiting for re-ranking
    return response["hits"]["hits"][:size]
