from src.services.elastic_query_service import browse_categories_query

def get_all_categories(es, INDEX_NAME):
    """
    Retrieve all unique categories from the Elasticsearch index.

    Returns:
        list: A list of unique category names.
    """
    body = browse_categories_query()

    response = es.search(
        index=INDEX_NAME,
        body=body
    )

    categories_result = [bucket for bucket in response['aggregations']['categories']['buckets']]
    return categories_result