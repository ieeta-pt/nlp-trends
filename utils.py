import os
import json
def walk_tree_tuple(folder):
    for conf_base_name in os.listdir(folder):
        for year in filter(lambda x: os.path.isdir(os.path.join(folder, conf_base_name, x)) and not x.startswith(".ipy"), os.listdir(os.path.join(folder, conf_base_name))):
            for track in os.listdir(os.path.join(folder, conf_base_name, year)):
                yield conf_base_name, year, track

def walk_tree(folder):
    for conf_base_name, year, track in walk_tree_tuple(folder):
        yield os.path.join(folder, conf_base_name, year, track)

def dataloader(files, base_dir):

    data = dict()
    for file in files:
        with open(base_dir+"/"+file) as f:
            json_data = json.load(f)
            for i in range(len(json_data)):
                
                json_data[i]["path"] = "conferences/"+json_data[i]["conf"]+"/"+json_data[i]["year"]+"/"+json_data[i]["track"]+"/"+json_data[i]["paper_id"]
            data[file.split('.')[0]] = json_data

    return data