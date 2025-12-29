from config import config
from src.services.llm_reranking_services import rerank_elasticsearch_results

CACHE_INDEX = config.CACHE_INDEX

def set_cached_results(query, results_to_rerank, _type, es):

    reranked_ids = rerank_elasticsearch_results(query, results_to_rerank)

    cache_object = {
        "user_query": query,
        "cached_product_ids": reranked_ids,
        "_type": _type
    }

    response = es.index(
        index=CACHE_INDEX,
        document=cache_object
    )

    return response