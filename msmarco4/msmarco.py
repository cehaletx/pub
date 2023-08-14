from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import openai
import os
import queries

ELASTIC_CLOUD_ID = os.getenv('ELASTIC_CLOUD_ID')
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ES_INDEX = 'my-index'

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configure Elasticsearch
es = Elasticsearch(cloud_id=ELASTIC_CLOUD_ID, basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD))

# Configure OpenAI
openai.api_key = OPENAI_API_KEY


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    # Retrieve the user input from the form

    elser = request.form.get('elser')
    bm25 = request.form.get('BM25')
    hybrid = request.form.get('hybrid')
    rrf = request.form.get('rrf')

    query = request.form['query']
    elser_boost = 0 if request.form['elser_boost'] == '' else int(request.form['elser_boost'])
    bm25_boost = 0 if request.form['BM25_boost'] == '' else int(request.form['BM25_boost'])

    if elser_boost or bm25_boost or hybrid:
        # Hybrid search
        if elser_boost == 0:
            elser_boost = 1
        if bm25_boost == 0:
            bm25_boost = 1
        results_hybrid = queries.hybrid_search(query, elser_boost, bm25_boost, es, ES_INDEX)
        paragraphs_hybrid = [hit['_source']['text'] for hit in results_hybrid['hits']['hits']]
        response_hybrid = queries.generate_text(paragraphs_hybrid, query, openai)
    else:
        results_hybrid = None
        response_hybrid = None

    if bm25:
        results_bm25 = queries.search_documents(query, es, ES_INDEX)
        paragraphs = [hit['_source']['text'] for hit in results_bm25['hits']['hits']]
        response_bm25 = queries.generate_text(paragraphs, query, openai)
    else:
        results_bm25 = None
        response_bm25 = None

    if elser:
        results_elser = queries.e_search_documents(query, es, ES_INDEX)
        paragraphs_e = [hit['_source']['text'] for hit in results_elser['hits']['hits']]
        response_elser = queries.generate_text(paragraphs_e, query, openai)
    else:
        results_elser = None
        response_elser = None

    if rrf:
        results_rff = queries.rrf(query, ES_INDEX)
        paragraphs_rff = [hit['_source']['text'] for hit in results_rff['hits']['hits']]
        response_rff = queries.generate_text(paragraphs_rff, query, openai)
    else:
        results_rff = None
        response_rff = None

    return render_template('search.html', query=query, results_hybrid=results_hybrid, response_hybrid=response_hybrid,
                           results_bm25=results_bm25,
                           response_bm25=response_bm25, results_elser=results_elser, response_elser=response_elser,
                           results_rff=results_rff, response_rff=response_rff)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
