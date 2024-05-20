import requests
from lxml import html, etree

import click
import os
import re
import json
from tqdm import tqdm
from utils import walk_tree
import jellyfish
from pylatexenc.latex2text import LatexNodes2Text

LATEXNODE = LatexNodes2Text()
SYMBLOLS = ["-", "-","\\", "/", "^", "&","$", "*", ":", "[", "]", "(", ")", "{", "}"]

TRANSLATION = str.maketrans({sym:" " for sym in SYMBLOLS})

def build_query(paper_title):
    return " ".join(paper_title.lower().translate(TRANSLATION).split())

def get_citations_from_semantic(paper_title):
    try:

        headers = {'content-type': 'application/json', "x-api-key": open(".api").readline()}
        base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {"query": build_query(paper_title), "limit": 5, "fields": "citationCount,title"}
        
        r = requests.get(base_url, headers=headers, params=params)
    except Exception as e:
        return None

    json_data = r.json()
    
    list_papers = []
    if "data" in json_data:
        for found_paper in json_data["data"]:
            if found_paper["title"]==paper_title:
                return found_paper["citationCount"]
            else:
                list_papers.append((jellyfish.jaro_similarity(paper_title.lower(), LATEXNODE.latex_to_text(found_paper["title"]).lower()), found_paper["title"], found_paper["citationCount"]))
                # compute jaro distance
    
        best_candidate_paper = max(list_papers, key=lambda x:x[0])
    
        if best_candidate_paper[0]>0.75:
            print(f"Not found exact match for {repr(paper_title)}, but {repr(best_candidate_paper[1])} was accepted with {best_candidate_paper[0]} matching score.")
            return best_candidate_paper[-1]
    
    
        # no match available
        print(f"DISCARDED: Match not found for {repr(paper_title)}, closest one was {repr(best_candidate_paper[1])} with {best_candidate_paper[0]} matching score.")

    print(json_data)
    return None
    
        
        

@click.command()
@click.option("--folder", default="conferences")
@click.option("--progress", default=True)
def main(folder, progress):

    fail_citations = []
    
    total = None
    if progress:
        total = 0
        # count number of papers
        for track_path in walk_tree(folder):
            with open(os.path.join(track_path, "papers_ids_titles.json")) as f:
                proceedings_papers = json.load(f)
            total += len(proceedings_papers)

    print(total)
    
    with tqdm(total=total) as pBar:
        for track_path in walk_tree(folder):
            
            with open(os.path.join(track_path, "papers_ids_titles.json")) as f:
                proceedings_papers = json.load(f)

            for paper_id, paper_data in proceedings_papers.items():

               
                citations = get_citations_from_semantic(paper_data["title"])
                if citations is not None:
                    paper_data |= {
                        "citations": int(citations)
                    }
                else:
                    _title = paper_data["title"]
                    print(f"Fail to get citation for paper {repr(_title)} | query {repr(build_query(_title))}")
                    fail_citations.append((os.path.join(track_path, paper_id), _title))
                pBar.update(1)
                
            # write the changes to file
            with open(os.path.join(track_path, "papers_ids_titles.json"), "w") as fOut:
                json.dump(proceedings_papers, fOut)

    with open("paper_get_citations_fail.txt", "w") as fFail:
        for path, title in fail_citations:
            fFail.write(f"{path}\t{title}\n")
        

if __name__ == '__main__':
    main()
    #pass