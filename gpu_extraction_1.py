from utils import walk_tree_tuple
import json
import os
from tqdm import tqdm
import re
from gpu_identifier_1_v1 import lookup_gpu, lookup_tpu


GPU_KEYWORDS_LIST=["rtx", "gpu", "nvidia", " tpu", "tesla", "quadro", "geforce", "gtx"]
FRAMWORK_KEYWORDS_LIST = ["tensorflow", "pytorch", " jax", " caffe", " theano", "keras" , "xgboost", "huggingface", "sci-kit learn", "scikit-learn", "sklearn"]
MAX_CHARS_FOR_CONTEXT=500




def find_context_for_index(text, index, max_chars=300):

    # use longer start indexes
    _right_index = text.find(".", index+1)
    if _right_index == -1:
        right_index = len(text)
    else:
        right_index = _right_index
        
    _left_index = text.rfind(".", 0, index)
    if _left_index == -1:
        left_index = 0
    else:
        left_index = _left_index    

    
    while right_index-left_index<max_chars:

        if _right_index == -1 and _left_index == -1:
            break
        
        _right_index = text.find(".", right_index+1)
        if _right_index != -1:
            right_index = _right_index
        
        _left_index = text.rfind(".", 0, left_index)
        if _left_index != -1:
            left_index = _left_index

        

    match_index = index - left_index
    #print(right_index, left_index, right_index-left_index, _right_index, _left_index)
    return text[left_index: right_index], match_index


def get_matches(text, keywords, year, paper_id, conf, track, framework):
    matches = []
    
    for keyword in keywords:
        if (key_match:=text.find(keyword))!=-1:
            gpu  = None
            match_context, key_match = find_context_for_index(text, key_match, max_chars=MAX_CHARS_FOR_CONTEXT)
            
            if framework:
                matches.append({
                "paper_id": paper_id,
                "year": year,
                "conf": conf,
                "track": track,
                "match_context": match_context, 
                "index": key_match,
                "keyword": keyword,
                })

            
            else:
                if keyword == ' tpu':
                    gpu = lookup_tpu(match_context)
                else:
                    gpu = lookup_gpu(match_context)
                    
                matches.append({
                    "paper_id": paper_id,
                    "year": year,
                    "conf": conf,
                    "track": track,
                    "gpu": gpu,
                    "match_context": match_context, 
                    "index": key_match,
                    "keyword": keyword,
                })
    return matches


def paper_get_keywords(paper_data, keywords_list, year, paper_id, conf, track, framework ):

    matches = []
    matches_sentences = []
    _abstract =  paper_data["abstract"].lower()
    matches.extend(get_matches(_abstract, keywords_list, year, paper_id, conf, track, framework))
        
    for section in paper_data["sections"]:
        matches.extend(get_matches(section["text"].lower(), keywords_list, year, paper_id, conf, track, framework))

        
    if "full_text" in paper_data:
        i=0
        for i in range(10, len(paper_data["full_text"]) - 10,20):
            matches_sentences.extend(get_matches(' '.join(paper_data["full_text"][i-10: i+10]).lower(), keywords_list, year, paper_id, conf, track, framework))
            
        matches_sentences.extend(get_matches(' '.join(paper_data["full_text"][i-10:]).lower(), keywords_list, year, paper_id, conf, track, framework))

 df is skeptical at best
    return matches, matches_sentences

folder = "conferences"
total = 0
limit_year = 2022


        
def iterating_tree_files_from_folder(folder):
    for conf_base_name, year, track in walk_tree_tuple(folder):
        if int(year) <= limit_year:
            with open(os.path.join(folder,conf_base_name, year, track, "papers_ids_titles.json")) as f:
                proceedings_papers = json.load(f)
                yield proceedings_papers, conf_base_name, year, track

# count number of papers
for proceedings_papers, _, _, _ in iterating_tree_files_from_folder(folder):
    total += len(proceedings_papers)
print(total)

def main():

    gpu_matches_full, gpu_matches_sen, fw_matches_full, fw_matches_sen = [], [], [], []
    papers_matched = set()
    
    with tqdm(total = total) as pBar:
        for proceedings, conf_base_name, year, track in iterating_tree_files_from_folder(folder):
            
            for paper_id in proceedings.keys():
                paper_id, _ = os.path.splitext(paper_id)
                paper_id = f"{paper_id}.json"
    
                paper_path = os.path.join(folder, conf_base_name, year, track, paper_id)
                
                if os.path.exists(paper_path):
                    with open(paper_path) as fPaper:
                        paper_data = json.load(fPaper)

                    #paper_match = {"paper_path": paper_path, "title": paper_data["title"]}
                    _gpu_matches_full, _gpu_matches_sen = paper_get_keywords(paper_data, GPU_KEYWORDS_LIST, year, paper_id,conf_base_name,track, False)
                    _fw_matches_full, _fw_matches_sen = paper_get_keywords(paper_data, FRAMWORK_KEYWORDS_LIST, year, paper_id,conf_base_name,track,True)
                    
                    
                    if  _gpu_matches_full:
                        gpu_matches_full.extend(_gpu_matches_full)
                        papers_matched.add(paper_path)
                    if  _gpu_matches_sen:
                        gpu_matches_sen.extend(_gpu_matches_sen)
                        papers_matched.add(paper_path)
                    if  _fw_matches_full:
                        fw_matches_full.extend(_fw_matches_full)
                        papers_matched.add(paper_path)
                    if  _fw_matches_sen:
                        fw_matches_sen.extend(_fw_matches_sen)
                        papers_matched.add(paper_path)
                else:
                    continue

                pBar.update(1)
                #print(f"{paper_path} not found")

    
    with open('output/gpu_matches_full.json', 'w') as f1:
        json.dump(gpu_matches_full, f1) 

    with open('output/gpu_matches_sen.json', 'w') as f2:
        json.dump(gpu_matches_sen, f2) 

    with open('output/fw_matches_full.json', 'w') as f3:
        json.dump(fw_matches_full, f3) 

    with open('output/fw_matches_sen.json', 'w') as f4:
        json.dump(fw_matches_sen, f4) 

    with open('output/papers_matched.json', 'w') as f5:
        json.dump(list(papers_matched), f5) 


main()