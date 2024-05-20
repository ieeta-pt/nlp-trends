import requests
from lxml import html, etree

import click
import os
import re
import json
from tqdm import tqdm
def get_citations_from_scholar(paper_title):
    try:
        base_url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={paper_title}&btnG="
        
        content = requests.get(base_url.replace(" ","+")).content.decode("latin-1")
        
        tree = html.document_fromstring(content)
        
        main_div = tree.body.get_element_by_id("gs_res_ccl_mid")
        
        paper_citation_txt = main_div.getchildren()[0].getchildren()[1].getchildren()[-1].getchildren()[2].text_content()
        
        citations = re.findall(r'\d+', paper_citation_txt)[0]
    except Exception as e:
        print("Citation for", paper_title, "NOT FOUND")
        
        raise e

    return citations


@click.command()
@click.option("--folder", default="conferences")
@click.option("--update", default=False)
@click.option("--progress", default=True)
def main(folder, update, progress):
    total = None
    if progress:
        total = 0
        # count number of papers
        for conf_base_name in os.listdir(folder):
            for year in filter(lambda x: os.path.isdir(os.path.join(folder, conf_base_name,x)), os.listdir(os.path.join(folder, conf_base_name))):
                for track in os.listdir(os.path.join(folder, conf_base_name, year)):
                    total += len(os.listdir(os.path.join(folder, conf_base_name, year, track)))-1

    print(total)
    
    with tqdm(total=total) as pBar:
        for conf_base_name in os.listdir(folder):
            for year in filter(lambda x: os.path.isdir(os.path.join(folder, conf_base_name,x)), os.listdir(os.path.join(folder, conf_base_name))):
                for track in os.listdir(os.path.join(folder, conf_base_name, year)):
                    
                    with open(os.path.join(folder, conf_base_name, year, track, "papers_ids_titles.json")) as f:
                        proceedings_papers = json.load(f)
                        
                    for paper_id, paper_data in proceedings_papers.items():
                        if isinstance(paper_data, dict):
                            paper_title = paper_data["title"]
                            if not update:
                                continue
                        else:
                            paper_title = paper_data
                                
                        proceedings_papers = {
                            "title": paper_title,
                            "citations": int(get_citations_from_scholar(paper_title))
                        }
                        pBar.update(1)
                        
                    # write the changes to file
                    with open(os.path.join(folder, conf_base_name, year, track, "papers_ids_titles.json"), "w") as fOut:
                        json.dump(proceedings_papers, fOut)

if __name__ == '__main__':
    #main()
    pass