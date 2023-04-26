#!/usr/bin/python3
#--------------------------------------------------------------------------------
# This script has a function defined to connect to elasticsearch and get cluster
# stats, to find total docs, and total size, then calculate an average doc size.
# Once we have an average doc size, it finds how many docs on each of the last N
# days and multiplies by average doc size.  Where N is a parameter you pass 
#--------------------------------------------------------------------------------
import sys
from datetime import datetime
from datetime import timedelta
import re
import time
import json
from elasticsearch import Elasticsearch
import warnings
warnings.filterwarnings("ignore")
#--------------------------------------------------------------------------------
# not doing any checking but let's get the command line arg. expecting an
# integer which is number of days of ingest to calculate
#--------------------------------------------------------------------------------
last_n_days = int( sys.argv[1] )
#--------------------------------------------------------------------------------
# direct connect to elasticsearch host, can be a list
#--------------------------------------------------------------------------------
#es = Elasticsearch(
#  ['localhost:9200'],
#  api_key=(""),
#  # turn on SSL
#  use_ssl=True,
#  # no verify SSL certificates
#  verify_certs=False,
#  # don't show warnings about ssl certs verification
#  ssl_show_warn=False
#)
#--------------------------------------------------------------------------------
# if you want to connect to cloud...
#--------------------------------------------------------------------------------
es = Elasticsearch(
    cloud_id="",
    basic_auth=("elastic", "")
)
class doubleQuoteDict(dict):
  def __str__(self):
    return json.dumps(self)
  def __repr__(self):
    return json.dumps(self)
# OK, let's get the cluster stats, for the total docs and total to calculate the average doc size.
resp = es.cluster.stats()
total_docs = int( resp[ "indices" ][ "docs" ][ "count" ])
print ( "total docs = " + str( total_docs ) )
total_data_set_size_in_bytes = int(resp[ "indices" ][ "store" ][ "total_data_set_size_in_bytes" ])
print ( "total_data_set_in_bytes = " + str( total_data_set_size_in_bytes ) )
avg_size = resp[ "indices" ][ "store" ][ "total_data_set_size_in_bytes" ] / resp[ "indices" ][ "docs" ][ "count" ]
print ( "average doc size = " + str( avg_size ) )
while( last_n_days >= 1 ):
  date_n1_days_ago = datetime.now() - timedelta( days=(last_n_days+1) )
  date_n_days_ago = datetime.now() - timedelta( days=last_n_days )
  range_query = { 
    'range': {
      'timestamp': { 
        'gte': date_n1_days_ago.strftime("%Y-%m-%dT00:00:00"), 
        'lte': date_n_days_ago.strftime("%Y-%m-%dT00:00:00")
      }
    }
  }
  #range_json = json.loads( range_query )
  print ( json.dumps(range_query) )
  resp = es.search(index="*",query=doubleQuoteDict(range_query),params={"track_total_hits":"true"})
  print( date_n_days_ago )
  print("%d docs " % resp['hits']['total']['value'])
  gigs = (resp['hits']['total']['value'] * avg_size) / 1024 / 1024 / 1024
  mb = (resp['hits']['total']['value'] * avg_size) / 1024 / 1024 
  print("in gigs = " + str(gigs) + ", or in mb = " + str(mb) )
  last_n_days = last_n_days - 1