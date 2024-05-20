import os
import openai
import json

with open ("openai-api-key.txt") as f:
    openai_key = f.readline()
    
openai.api_key = openai_key

files = ["gpu_matches_sen.json","gpu_matches_full.json"] 
base_dir = "output"
data = dict()
for file in files:
    with open(base_dir+"/"+file) as f:
        json_data = json.load(f)
        for i in range(len(json_data)):            
            json_data[i]["path"] = "conferences/"+json_data[i]["conf"]+"/"+json_data[i]["year"]+"/"+json_data[i]["track"]+"/"+json_data[i]["paper_id"]
            json_data[i]["source"] = file
            
        data[file.split('.')[0]] = json_data

errors = {}

for i in data["gpu_matches_sen"]:

    context = i['match_context']
    
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"""You are a machine learning expert. Your goal is to extract correct information from a given CONTEXT and answer the  QUESTION correctly. When in doubt use the value -1.CONTEXT:{context} QUESTION: What is the total training time of the models, explaing reasoning, return only a json: {{total_time: NUMBER, unit: MINUTE/HOURS/DAYS, gpus:[{{gpu: GPU_NAME, number_of_gpus: NUMBER }},...  ]}}"""}])
    out = chat_completion['choices'][0]['message']['content']
    
    left_index = out.find('{')
    right_index = out.rfind('}')+1
    if left_index == -1 or right_index == -1:
        out_json = {"error": -1}
        errors.add(chat_completion)
    else:
        out_json = json.loads(out[left_index:right_index])
    
    i['chatgpt'] =  out_json


with open('output/openai/gpu_matches_full_openai.json', 'w') as f:
    json.dump(data["gpu_matches_sen"], f) 

with open('output/openai/gpu_matches_full_openai_errors.json', 'w') as f:
    json.dump(errors, f) 


errors = {}

for i in data["gpu_matches_full"]:

    context = i['match_context']
    
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"""You are a machine learning expert. Your goal is to extract correct information from a given CONTEXT and answer the  QUESTION correctly. When in doubt use the value -1.CONTEXT:{context} QUESTION: What is the total training time of the models, explaing reasoning, return only a json: {{total_time: NUMBER, unit: MINUTE/HOURS/DAYS, gpus:[{{gpu: GPU_NAME, number_of_gpus: NUMBER }},...  ]}}"""}])
    out = chat_completion['choices'][0]['message']['content']
    
    left_index = out.find('{')
    right_index = out.rfind('}')+1
    if left_index == -1 or right_index == -1:
        out_json = {"error": -1}
        errors.add(chat_completion)
    else:
        out_json = json.loads(out[left_index:right_index])
    
    i['chatgpt'] =  out_json
    





with open('output/gpu_matches_sen_openai.json', 'w') as f:
    json.dump(data["gpu_matches_full"], f) 


with open('output/openai/gpu_matches_full_openai_errors.json', 'w') as f:
    json.dump(errors, f) 





