from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import openai
import os

ELASTIC_CLOUD_ID = os.getenv('ELASTIC_CLOUD_ID')
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ES_INDEX = 'bible-kjv-enriched-single-field'

app = Flask(__name__)

# Configure Elasticsearch
#es = Elasticsearch(hosts=['http://localhost:9200'])
es = Elasticsearch(cloud_id=ELASTIC_CLOUD_ID, basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD))

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Retrieve the user input from the form
    query = request.form['query']

    # Perform the Elasticsearch search
    results = search_documents(query)

    # Extract the verse from the search results
    verses = [hit['_source']['verse'] for hit in results['hits']['hits']]

    # Use the verse as context for OpenAI
    response = generate_text(verses)

    # perform the Elasticsearch ELSER query
    results_e = e_search_documents(query)

    print(results_e)

    # Extract the verse from the search results
    verses_e = [hit['_source']['verse'] for hit in results_e['hits']['hits']]

    # Use the verse as context for OpenAI
    response_e = generate_text(verses_e)

    return render_template('search.html', query=query, results=results, response=response, results_e=results_e, response_e=response_e)

def search_documents(query):
    # Define the Elasticsearch search query
    search_query = {
        "match": {
            "verse": query
        }
    }

    # Execute the search query
    results = es.search(index=ES_INDEX, query=search_query)

    return results

def e_search_documents(query):
    # Define the Elasticsearch ELSER search query
    search_query = {
       "text_expansion":{
          "ml.tokens":{
             "model_id":".elser_model_1",
             "model_text":query
          }
       }
    }

    # Execute the search query
    results = es.search(index=ES_INDEX, query=search_query, fields=["reference","verse"], error_trace='true')

    return results

def generate_text(verses):
    # Join the verse into a single string
    context = ' '.join(verses)

    # Define the OpenAI prompt and generate the response
    prompt = "Given the following documents, please provide a response:\n" + context
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
        n=1,
        stop=None
    )

    return response.choices[0].text.strip()

if __name__ == '__main__':
    app.run()
