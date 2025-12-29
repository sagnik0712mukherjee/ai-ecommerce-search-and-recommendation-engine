from src.services.inventory_search_service import search_inventory
from config import config

def pdp_recommendations(item_name, item_pid, model, INDEX_NAME, es, num_recs=5):

    results = search_inventory(
        query=item_name,
        _from=0,
        size=num_recs+2,
        model=model,
        INDEX_NAME=INDEX_NAME,
        es=es,
        _type=config.recommendation_type
    )

    final_results = [
        x for x in results if x["_source"].get("product_id") != item_pid
    ][:num_recs]

    return final_results

