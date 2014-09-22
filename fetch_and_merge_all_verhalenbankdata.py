'''
Created on May 15, 2014

@author: iwemuiser
'''
import datetime
import time
import json_data_fetcher
import json
import pprint
import re
from config import EXPORT_DIR

date = datetime.date.today()
#date = "2014-09-09" #for testing purposes

data_dir = EXPORT_DIR

collector_data_from_omeka = data_dir +      "collector_omeka_json_data_" + str(date) + ".json"
narrator_data_from_omeka = data_dir +       "narrator_omeka_json_data_" + str(date) + ".json"
folktale_data_from_omeka = data_dir +       "folktale_omeka_json_data_" + str(date) + ".json"
geolocation_data_from_omeka = data_dir +    "geolocation_omeka_json_data_" + str(date) + ".json"

final_flat_file = data_dir +                "flat_folktale_data_" + str(date) + ".json"
final_flat_narrators = data_dir +           "flat_narrator_data_" + str(date) + ".json"
final_flat_collectors = data_dir +          "flat_collector_data_" + str(date) + ".json"


def determine_text_length(t):
    import re
    try:
        return len(re.findall("\w+", t))
    except:
        try:
            return len(re.findall("\w+", " ".join(t)))
        except:
            return -1

def classify_length(length):
    if length < 20:
        return ('<25', '1. Ongeveer een regel (< 25 woorden)')
    if length < 100:
        return ('25-100', '1. paar regels (< 100 woorden)')
    elif length < 250:
        return ('100-250', '2. meer, maar minder dan halve pagina (< 250 woorden)')
    elif length < 500:
        return ('250-500', '3. meer, maar minder dan een hele pagina (< 500 woorden)')
    elif length < 1000:
        return ('500-1000', '3. meer, maar minder dan 2 pagina\'s (< 1000 woorden)')
    else:
        return ('>1000', '4. meer dan 2 hele pagina\'s (>= 1000 woorden)')

def date_start_supplement(date):
    if date == "99-99-99": return None
    pattern = "^\d\d\d\d-\d\d-\d\d"
    date = re.match(pattern, date)
    if date:
        return date.group(0) + "T12:00:00Z"
    return None

def platsla(node, searchable_geo):
    platte_node = {"tags" : []}
    #adds the tags
    for tag in node['tags']: 
        platte_node['tags'].append(tag['name'])
    #adds the elements
    #elements need to be checked for repeating fields!
    for branch in node['element_texts']:
        new_name = branch["element"]["name"].lower().replace(" ", "_")
        if platte_node.has_key(new_name):
            # if node exists and value is list -> append to list
            if isinstance(platte_node[new_name], list):
                platte_node[new_name].append(branch["text"])
            #if node exists and value is string
            else:
                platte_node[new_name] = [platte_node[new_name], branch["text"]]
        else:
            #if the node does not exist -> just add as a string
            platte_node[new_name] = branch["text"]
    #adds item and omeka information
    platte_node['collectionid'] = node['collection']['id']
    platte_node["id"] = node["id"] 
    platte_node["url"] = node["url"]
    platte_node["public"] = node["public"]
    platte_node["featured"] = node["featured"]
    platte_node["added"] = node["added"]
    platte_node["modified"] = node["modified"]
    platte_node["item_type"] = node["item_type"]["name"]
    platte_node["url"] = node["url"]
    #adds geolocation information if exists
    if node.has_key('extended_resources'):
        if node['extended_resources'].has_key("geolocations"):
            print str(platte_node[u"id"]) + " -- " + str(node['extended_resources']["geolocations"]["id"])
            for i in searchable_geo[node['extended_resources']["geolocations"]["id"]]:
#                print i
                #dont add the id and url of geolocation
                if i == "id":
                    None
                elif i == "url":
                    None
                elif searchable_geo[node['extended_resources']["geolocations"]["id"]][i]:
                    platte_node[i] = searchable_geo[node['extended_resources']["geolocations"]["id"]][i]
    # determine the text length
    if 'text' in platte_node:
        text_length = determine_text_length(platte_node['text'])
    else:
        text_length = 0
    if platte_node.has_key('date'):
        if isinstance(platte_node['date'], list):
            platte_node['date_start'] = []
            for d in platte_node['date']:
                platte_node['date_start'].append(date_start_supplement(d))
        else:
            platte_node['date_start'] = date_start_supplement(platte_node['date'])
    platte_node['text_length'] = text_length
    platte_node['text_length_group'] = classify_length(text_length)[0]
    return platte_node

def merge_tales_and_locations():
    geo_readit = open(geolocation_data_from_omeka, "r")
    geo_jsoncontent = json.loads(geo_readit.read())
    searchable_geo = geo_lookup(geo_jsoncontent)
    tale_readit = open(folktale_data_from_omeka, "r")
    tale_jsoncontent = json.loads(tale_readit.read())
    print "Folktale JSON content read... Now calculating"
    i = 0;
    with open(final_flat_file, 'w') as f:
        f.write('[')
    for tale in tale_jsoncontent:
        i += 1
        tale = platsla(tale, searchable_geo)
        print str(i) + ": merging tales merged with geolocations: " + str(tale["id"])
        with open(final_flat_file, 'a') as f:
            if i > 1: f.write(',\n')
            json.dump(tale, f)
#        print pprint.pprint(tale)
    with open(final_flat_file, 'a') as f:
        f.write(']')
    return tale_jsoncontent

def merge_items_and_locations(item_data_from_omeka, final_flat_items):
    geo_readit = open(geolocation_data_from_omeka, "r")
    geo_jsoncontent = json.loads(geo_readit.read())
    searchable_geo = geo_lookup(geo_jsoncontent)
    readit = open(item_data_from_omeka, "r")
    jsoncontent = json.loads(readit.read())
    print "Narrator JSON content read... Now calculating"
    i = 0;
    with open(final_flat_items, 'w') as f:
        f.write('[')
    for item in jsoncontent:
        i += 1
        item = platsla(item, searchable_geo)
        with open(final_flat_items, 'a') as f:
            if i > 1: f.write(',\n')
            json.dump(item, f)
        print str(i) + ": merging narrators merged with geolocations: " + str(item["id"])
    with open(final_flat_items, 'a') as f:
        f.write(']')
    return jsoncontent

def geo_lookup(geo_jsoncontent):
    geo_lookup_array = {}
    for i in geo_jsoncontent:
        geo_lookup_array[i["id"]] = i
    return geo_lookup_array

if __name__ == '__main__':
    main_start = time.time()
    date = datetime.date.today()

    # get the locations
    #this step can be turned off if the files are fetched
    json_data_fetcher.write_db_to_file(geolocation_data_from_omeka, get_type = "geolocations", collection = None)
    print "Geolocation data downloaded in\t" + str(time.time() - main_start) + " seconds = " + str((time.time() - main_start) / 60) + " minuten"

    # get the tales
    #this step can be turned off if the files are fetched
    json_data_fetcher.write_db_to_file(folktale_data_from_omeka, get_type = "items", collection = 1)
    print "Folktale data downloaded in\t" + str(time.time() - main_start) + " seconds = " + str((time.time() - main_start) / 60) + " minuten"

    # get the narrators
    #this step can be turned off if the files are fetched
    json_data_fetcher.write_db_to_file(narrator_data_from_omeka, get_type = "items", collection = 4)
    print "Narrator data downloaded in\t" + str(time.time() - main_start) + " seconds = " + str((time.time() - main_start) / 60) + " minuten"

    # get the collectors
    #this step can be turned off if the files are fetched
    json_data_fetcher.write_db_to_file(collector_data_from_omeka, get_type = "items", collection = 9)
    print "Collector data downloaded in\t" + str(time.time() - main_start) + " seconds = " + str((time.time() - main_start) / 60) + " minuten"

    #merge the locations with the tales
    print "Starting file merge..."

    #this function also writes to the output file
    merged_data = merge_tales_and_locations()
    merge_items_and_locations(narrator_data_from_omeka, final_flat_narrators)
    merge_items_and_locations(collector_data_from_omeka, final_flat_collectors)

    print "Completed in\t" + str(time.time() - main_start) + " seconds = " + str((time.time() - main_start) / 60) + " minuten"