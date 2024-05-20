import re
import pandas as pd

#problems:
# picks up number of params as gpu for example ", 2019) while the layoutlm baselines are implemented with the codebase in layoutlm's official repository 4 . we use 8 v100 gpus with a batch size of 10 per gpu. it takes 5 hours to fine-tune 1 epoch on the 400k document pages {'v100', '400'}"

#stems = ["tpu", "gpu", "nvidia", "geforce", "rtx", "gtx", "tesla", "quadro"]

gpu =  pd.read_csv("gpus_v3.csv")

def lookup_gpu(context): 
    """
    context: text string that we want to identify gpus in

    given ther contecxt return a set of possible gpu candidates
    """
    context = context.lower()
    #regex
    #remove hyphens (people used v-100)
    context = re.sub("-", "", context) 
    #add a space for rtx3080 to be rtx 3080
    context = re.sub("(rtx)(\d+)", r"\1 \2", context) 
    context = re.sub("(gtx)(\d+)", r"\1 \2", context)
    #add  a space for 2070ti to be 2070 ti
    context = re.sub("(\d+)(ti)", r"\1 \2", context) 
 

    matched  = []
    for candidate in gpu.iterrows():
        #in the dataframe each row has 2 possible candidates, taken from 2 sources. 
        #filtered_name_GPU is more specific and is checked first
   
        candidate1 = str(candidate[1]["filtered_name_GPU"])
        candidate2 = str(candidate[1]["filtered_name_product"])

        
        if candidate1 in context and candidate1 != 'nan':
            matched.append(candidate1)
        elif candidate2 in context and candidate2 != 'nan':
            matched.append(candidate2)
    matched = set(matched)

    contained = []
    #detect subsets of gpus example a10 over a100
    #probably inefficient but needed to fix issues
    for i in matched:
        for j in matched: 
            if i in j and i != j:
                contained.append(i)

    #remove subsets of gpus example a10 over a100            
    for i in contained:
        if i in matched:
            matched.remove(i)
            
    return list(matched)

def lookup_tpu(context): 
    #untested codea
    """
    context: text string that we want to identify tpu in

    returns the version of the tpu, assumes v1 if not specified
    """

    
    if "v2" in context: 
        return ["tpu v2"]
    elif "v3" in context: 
        return ["tpu v3"]
    elif "v4" in context: 
        return ["tpu v4"]
    else: 
        return ["tpu v1"]

    


