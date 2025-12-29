def search_query(query_vector, _from, size, _source = {"excludes": ["embedding"]}, cat_pred = None, sub_cat_pred = None, sub_sub_cat_pred = None, sub_sub_sub_cat_pred = None):

    body = {
        "_source": _source,
        "size": size,
        "from": _from,
        "knn": {
            "field": "embedding",
            "query_vector": query_vector,
            "k": 75,
            "num_candidates": 100
        }
    }

    if cat_pred and sub_cat_pred and sub_sub_cat_pred and sub_sub_sub_cat_pred:
        body["query"] = {
            "bool": {
                "should": [
                    {
                        "term": {
                            "category": {
                                "value": cat_pred,
                                "boost": 1.5
                            }
                        }
                    },
                    {
                        "term": {
                            "sub_category": {
                                "value": sub_cat_pred,
                                "boost": 2.0
                            }
                        }
                    },
                    {
                        "term": {
                            "sub_sub_category": {
                                "value": sub_sub_cat_pred,
                                "boost": 3.0
                            }
                        }
                    },
                    {
                        "term": {
                            "sub_sub_sub_category": {
                                "value": sub_sub_sub_cat_pred,
                                "boost": 4.0
                            }
                        }
                    }
                ],
                "minimum_should_match": 0
            }
        }

    return body


def browse_categories_query():

    body = {
        "size": 0,
        "aggs": {
            "categories": {
                "terms": {
                    "field": "category",
                    "size": 1000
                }
            }
        }
    }

    return body


def browse_items_query(size = 15, _source = {"excludes": ["embedding"]}):

    body = {
        "_source": _source,
        "size": size,
        "query": {
            "match_all": {}
        }
    }

    return body


def get_items_by_id_query(product_ids, _source = {"excludes": ["embedding"]}):
    body = {
        "_source": _source,
        "size": len(product_ids),
        "query": {
            "terms": {
                "product_id": product_ids
            }
        }
    }

    return body


def get_cache_query(query, _type):
    body = {
        "size": 1,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "user_query.keyword": query
                        }
                    },
                    {
                        "term": {
                            "_type.keyword": _type
                        }
                    }
                ]
            }
        }
    }

    return body