#!/usr/bin/python
'''
Created on Sep 11, 2013

@author: iwemuiser
'''
import json
import pprint
from omeka_client import OmekaClient
import re
import string
import time
import datetime
from config import YOUR_OMEKA_API_KEY, CLIENT_BASE, RESULTS_PER_PAGE

def write_db_to_file(json_file_name, get_type = "items", collection = 1):
    
    api_key = YOUR_OMEKA_API_KEY

    # Omeka items are part of a collection. The number of the collection to download
    # (1 = folktales collection)

    per_page = RESULTS_PER_PAGE
    
    client_base = CLIENT_BASE 
    
    pp = pprint.PrettyPrinter(depth=8)
    client = OmekaClient(client_base, None)
    
    # GET /items
    # For more information on the API:
    # http://omeka.readthedocs.org/en/latest/Reference/api/index.html
    # pretty_print will result in a larger, yet more readable database
    if (api_key):
        if (collection):
            print "api key" + api_key + " AND collection"
            response, content = client.get(get_type, query = {"collection" : collection, "page" : "1", "key" : api_key, "pretty_print": ""})
        else:
            print "api key" + api_key + " AND NO collection"
            response, content = client.get(get_type, query = {"page" : "1", "key" : api_key, "pretty_print": ""})
    else:
        if (collection):
            print "NO api key AND collection"
            response, content = client.get(get_type, query = {"collection" : collection, "page" : "1", "pretty_print": ""})
        else:
            print "NO api key AND NO collection"
            response, content = client.get(get_type, query = {"page" : "1", "pretty_print": ""})
 
    print response
 
    there_is_more = True
    temp_counter = 0

    with open(json_file_name, "w") as f:
        f.write("[")
        f.write(content[1:-1])
    
    while there_is_more:
        start = time.time()
        temp_counter += 1
        # OR DOWNLOADING A SUBSET FOR TESTING
#        if temp_counter > 3: there_is_more = False
        pages = {}
        for i in string.split(response["link"], ", "):
            splitted = string.split(i, "; ")
            pages[splitted[1]] = splitted[0]
        if pages.has_key('rel="next"'):
            response, content = client.get_page(pages['rel="next"'][1:-1]+"&key=4219501c9c5602989877edbeacf6d50118d4c698") #key must be resupplied... omeka messes up count
            if content:
                with open(json_file_name, "a") as feedsjson:
                    feedsjson.write(", ")
                    feedsjson.write(content[1:-1])
            else: there_is_more = False
        else: there_is_more = False
        per_item = time.time() - start
        print "Page", temp_counter, "of", (int(response["omeka-total-results"]) / per_page), ". About", (per_item * ((int(response["omeka-total-results"])/50) - temp_counter) / 60), "minutes left"

    with open(json_file_name, "a") as f:
        f.write("]")
        
    
if __name__ == '__main__':
    main_start = time.time()
    
    date = datetime.date.today()

    # local file for storing the JSON data
    json_file_name = "/Users/iwemuiser/Data/databases/json_vb_db/folktale_omeka_json_data_" + str(date) + ".json"
    print json_file_name

    write_db_to_file(json_file_name, get_type = "items", collection = 3)
    
    print "Downloaded in\t" + str(time.time() - main_start) + " seconds = " + str((time.time() - main_start) / 60) + " minuten"