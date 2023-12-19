### cehaletx public repository
## my shared projects

# - last-N-days
A python script to query a cluster for N days of ingest.  [[Work in Progress]]

Note: This first version looks at the average doc size across the cluster, and then goes for each of the last N days, and finds a doc count, and multiplies out to establish an ingest rate.

# - openai-elastic-examples
a couple examples of datasets which can be uploaded to elasticsearch, with a python UI that will let you query elasticsearch and also pass contents to openAI for an example of Retrieval-Augmented Generation (RAG) 

these scripts require elasticsearch, flask, os, and openai libraries.  use pip install for these

pip install elasticsearch
pip install flask 
pip install os
pip install openai

# - msmarco4 is a new version modified by Jenny Morris, which adds options for using RRF in the queries
The RRF option combines vector and bm25 results in elastic using RF, which is Reciporical Rank Fusion.

# ILM_example_dev_tools_code.txt
added a txt file with some working DevTools example commands to showcase BASIC (pre Data stream) ILM Functionality
