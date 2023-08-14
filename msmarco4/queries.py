import requests
import os

RRF_USERNAME = os.getenv('RRF_USERNAME')
RRF_PASSWORD = os.getenv('RRF_PASSWORD')
RRF_URL = os.getenv('RRF_URL')


def search_documents(query, es, ES_INDEX):
    # BM25
    # Define the Elasticsearch search query
    search_query = {
        "match": {
            "text": query
        }
    }

    # Execute the search query
    results = es.search(index=ES_INDEX, query=search_query)

    return results


def e_search_documents(query, es, ES_INDEX):
    # Elser
    # Define the Elasticsearch ELSER search query
    search_query = {
        "text_expansion": {
            "ml.tokens": {
                "model_id": ".elser_model_1",
                "model_text": query
            }
        }
    }

    # Execute the search query
    results = es.search(index=ES_INDEX, query=search_query, fields=["id", "text"], error_trace='true')

    return results


def generate_text(paragraphs, query, openai):
    # Join the paragraph into a single string
    context = ' '.join(paragraphs)

    # Define the OpenAI prompt and generate the response
    # prompt = "Given the following documents, please provide a response:\n" + context
    prompt = "Given the following documents, please provide a response: to this question \n" + query + " DOCS: " + context
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=2048,
        temperature=0.7,
        n=1,
        stop=None
    )
    return response.choices[0].text.strip()


def hybrid_search(query, elser_boost, bm25_boost, es, ES_INDEX):
    # Define your "should" conditions
    should_conditions = [
        {
            "text_expansion": {
                "ml.tokens": {
                    "model_text": query,
                    "model_id": ".elser_model_1",
                    "boost": elser_boost
                }
            }
        },
        {
            "query_string": {
                "query": query,
                "boost": bm25_boost
            }
        }
    ]

    # Create the "should" query
    should_query = {
        "bool": {
            "should": should_conditions
        }
    }

    # Combine "should" query with the "min_score" filter
    search_query = {
        "query": should_query,
        "min_score": 10
    }

    # Execute the query
    result = es.search(index=ES_INDEX, body=search_query)
    return result


def rrf(query, ES_INDEX):
    elasticsearch_url = 'https://111974ca1d6d4281b580c66911293249.us-central1.gcp.cloud.es.io'

    # Execute the search query
    query_body = {
        "sub_searches": [
            {
                "query": {
                    "match": {
                        "text": query
                    }
                }
            },
            {
                "query": {
                    "text_expansion": {
                        "ml.tokens": {
                            "model_text": query,
                            "model_id": ".elser_model_1"
                        }
                    }
                }
            }
        ],
        "rank": {
            "rrf": {
                "window_size": 50,
                "rank_constant": 25
            }
        }
    }

    # Make the request to Elasticsearch
    response = requests.get(f'{elasticsearch_url}/{ES_INDEX}/_search', json=query_body,
                            auth=(RRF_USERNAME, RRF_PASSWORD))
    return response.json()
