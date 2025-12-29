def prompt_for_reranking(original_query, data_to_rerank):

    optimised_data = "\n".join([f"ID: {item['product_id']} | Name: {item.get('name', '')} | Category Hierarchy: {' >> '.join([item.get('category',''), item.get('sub_category',''), item.get('sub_sub_category',''), item.get('sub_sub_sub_category')])}" for item in data_to_rerank])

    prompt = f"""

    Here is user's original query: {original_query}

    Here is the list of search results to be ranked:
    {optimised_data}

    In your response, just share the re-ranked list (array) of product IDs in order of relevance, and say nothing else. For example: [ID1, ID2, ID3, ID4]
    - No markdown
    - No ```code``` blocks or ```JSON``` blocks
    - No additional text
    - No explanations
    - No creation of new product IDs
    - Do no remove any product ID from the provided list; all should be returned & reranked in new improved order.
    - Organise the results very well, for example, if there are 10 relevant results of two types of brands, then group them together in the ranking, brand-wise.
    - Relevance should be the only criteria for ranking. Most relevant result on top and rest to follow.

    """

    return prompt