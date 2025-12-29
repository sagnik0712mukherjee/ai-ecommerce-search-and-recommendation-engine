from openai import OpenAI
from src.services.ai_prompt_service import prompt_for_reranking
import json

# The client automatically picks up the OPENAI_API_KEY environment variable if not specified as client = OpenAI(api_key="your_api_key_here")
client = OpenAI()

def rerank_elasticsearch_results(original_query, data_to_rerank):

    parent_ids = [item['product_id'] for item in data_to_rerank]

    try:

        prompt = prompt_for_reranking(original_query, data_to_rerank)

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                            You are an expert search result ranker.
                            Given the original user query and a list of search results, your task is to rank the results based on their relevance to the query.
                            The most relevant results should be ranked highest followed by less relevant ones.
                            """
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        reranked_ids_str = response.choices[0].message.content.strip()
        reranked_ids = json.loads(reranked_ids_str)
    
    except Exception as e:

        print(f"Error during reranking: {e}")
        reranked_ids = parent_ids

    return reranked_ids