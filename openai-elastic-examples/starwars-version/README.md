use the text in this directory and ingest into your elasticsearch env
use the cheat sheet 5 step process to prep the data.

For this particular data set, the 5 step process is already done for you in this dev tools ready
snippet
# 
# Step 1 - Ingest the json in starwars-txt sub directory using kibana “Upload a File” name the index 
# starwars-novel
#
# check your text uploaded
GET starwars-novel/_search
#
# Step 2 - Make sure you have your ELSER Model turned on.  You can see 
# it in pipelines in Kibana Index Management for your index, or in 
# Machine Learning Data Models.
#
# Step 3 - create your mapping with rank features field.
PUT starwars-novel-enriched
{
  "mappings": {
    "properties": {
      "ml.tokens": {
        "type": "rank_features"
      },
      "text": {
        "type": "text"
      }
    }
  }
}  
# Step 4 - Create your pipeline to enrich the index with the ELSER
# created ml.tokens.
PUT _ingest/pipeline/elser-tokens-creation-starwars
{
  "processors": [
    {
      "inference": {
        "model_id": ".elser_model_1",
        "target_field": "ml",
        "field_map": {
          "paragraph": "text_field"
        },
        "inference_config": {
          "text_expansion": {
            "results_field": "tokens"
          }
        }
      }
    }]
}
GET _ingest/pipeline/elser-tokens-creation-starwars
# Step 5 - Reindex the original upload using your pipeline
POST _reindex?wait_for_completion=false
{
  "source": {
    "index": "starwars-novel",
    "size": 200
  },
  "dest": {
    "index": "starwars-novel-enriched",
    "pipeline": "elser-tokens-creation-starwars"
  }
}
# capture the task id and you can watch progress with the following command, be patient, it takes a
# little while.  look for "created" to equal your docs.
GET _tasks/<task_id>
# once that is completed you can start asking questions
GET starwars-novel-enriched/_search
{
   "query":{
      "text_expansion":{
         "ml.tokens":{
            "model_id":".elser_model_1",
            "model_text":"who was luke's uncle?"
         }
      }
   },
   "_source": ["paragraph"]
}
