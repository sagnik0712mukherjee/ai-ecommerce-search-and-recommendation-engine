from src.services.inventory_search_service import search_inventory


def search_catalog(user_query, _from, size, model, INDEX_NAME, es):

    results = search_inventory(
        query=user_query,
        _from=_from,
        size=size,
        model=model,
        INDEX_NAME=INDEX_NAME,
        es=es
    )

    return results