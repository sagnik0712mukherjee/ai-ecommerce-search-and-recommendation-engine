from src.services.elastic_query_service import browse_items_query

def get_all_items(es, INDEX_NAME, size = 15):

    body = browse_items_query(size)

    response = es.search(
        index=INDEX_NAME,
        body=body
    )

    return response["hits"]["hits"]