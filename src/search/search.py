from src.elastic_queries import search_query

def search_inventory(query, _from, size, model, INDEX_NAME, es):
    query_vector = model.encode(query).tolist()

    # get search intent
    search_intent_body = search_query(query_vector, 0, 5, ["category", "sub_category", "sub_sub_category","sub_sub_sub_category"])
    response_intent = es.search(
        index=INDEX_NAME,
        body=search_intent_body
    )
    res = response_intent["hits"]["hits"]

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

    revised_query = f"Item *{query}* is of category hierarchy {cat_pred} and {sub_cat_pred} and {sub_sub_cat_pred} and {sub_sub_sub_cat_pred}"
    revised_query_vector = model.encode(revised_query).tolist()

    body = search_query(revised_query_vector, _from, size, _source={"excludes": ["embedding"]}, cat_pred=cat_pred, sub_cat_pred=sub_cat_pred, sub_sub_cat_pred=sub_sub_cat_pred, sub_sub_sub_cat_pred=sub_sub_sub_cat_pred)

    response = es.search(
        index=INDEX_NAME,
        body=body
    )

    return response["hits"]["hits"]

