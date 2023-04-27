#!/usr/bin/python3
#--------------------------------------------------------------------------------
#  This is the  Version 2 of get-late-N-days, which will now look specifically
# at 3 particular index patterns rather than the whole cluster.
# The benefit of looking at these specifics, logs-*, metrics-*, and apm-* is they
# are the bulk of the data coming in for and observability cluster.
#
# will keep the old calculation for comparison.
#
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
#last_n_days = int( sys.argv[1] )
last_n_days = int (3)
#index_patterns=["logs-*","metrics-*","apm-*"]
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
#    cloud_id="",
#    basic_auth=("elastic", "")
    cloud_id="",
    basic_auth=("elastic", "")
)
class doubleQuoteDict(dict):
  def __str__(self):
    return json.dumps(self)
  def __repr__(self):
    return json.dumps(self)

# before looking at the previous N days, let's inspect cat indices * for a doc count, and avg size
#
#logs-* first
resp = es.cat.indices( index="*", format="json",bytes="b" )
#`print( resp )
temp_total_docs = 0
temp_total_pri = 0
new_avg_doc = 0
for each_index in resp:
  temp_total_docs+= int( each_index["docs.count"] )
  temp_total_pri+= int( each_index["pri.store.size"] )
new_avg_doc = temp_total_pri / temp_total_docs
print( "total docs = ", temp_total_docs)
print( "total pri size = ", temp_total_pri)
print ( "avg doc size = ", new_avg_doc )
while( last_n_days >= 1 ):
  date_n1_days_ago = datetime.now() - timedelta( days=(last_n_days+1) )
  date_n_days_ago = datetime.now() - timedelta( days=last_n_days )
  range_query = { 
    'range': {
      '@timestamp': { 
        'gte': date_n1_days_ago.strftime("%Y-%m-%dT00:00:00"), 
        'lte': date_n_days_ago.strftime("%Y-%m-%dT00:00:00")
      }
    }
  }
  #range_json = json.loads( range_query )
  print ( json.dumps(range_query) )
  resp = es.search(index="*",query=doubleQuoteDict(range_query),params={"track_total_hits":"true"})
  #print( date_n_days_ago )
  print("%d docs " % resp['hits']['total']['value'])
  gigs = (resp['hits']['total']['value'] * new_avg_doc) / 1024 / 1024 / 1024
  mb = (resp['hits']['total']['value'] * new_avg_doc) / 1024 / 1024 
  print("in gigs = " + str(gigs) + ", or in mb = " + str(mb) )
  last_n_days = last_n_days - 1