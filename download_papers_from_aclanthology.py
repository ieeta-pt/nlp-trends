import click

import requests

import pandas as pd
from lxml import etree, html

from collections import defaultdict
import os

import json
from tqdm import tqdm

def get_years_and_urls(base_url, stop_year):

    skip_words = {"workshop", "demonstration", "tutorial", "student", "industry"}
    
    page = requests.get(base_url).content.decode("utf-8")
    tree = html.document_fromstring(page)
    
    
    table_div = tree.body.get_element_by_id("main").getchildren()[-1]
    
    table = defaultdict(list)
    
    for row in table_div.getchildren():
        year = row.getchildren()[0].text_content()
        if int(year)<stop_year:
            break
        
        for pdf_proceddings in row.getchildren()[1].getchildren()[0].getchildren():
            a_el = pdf_proceddings.find("a")
            if not any([w in a_el.text_content().lower() for w in skip_words]):
                print("Accepted:", a_el.text_content())
                link = a_el.get("href")
                table[year].append({
                    "proceedings": a_el.text_content(),
                    "link": f"https://aclanthology.org/{link}"
                })
    
    return table

def get_papers_titles_and_ids(url, out_folder):
    
    page = requests.get(url).content.decode("utf-8")
    tree = html.document_fromstring(page)
    
    table_div = tree.body.get_element_by_id("main").getchildren()[-1]

    table = {}
    
    for i,title_p in enumerate(table_div.findall("p")):
        a_title_el = title_p.getchildren()[1].getchildren()[0].find("a")
        a_url_paper_el = title_p.getchildren()[0].getchildren()[0].get("href")
        
        title_article = a_title_el.text_content()

        if title_article.lower().startswith("proceedings"):
            continue
            
        article_id = a_title_el.get("href").rstrip("/").lstrip("/")
        article_path = f"{article_id}.pdf"
        
        table[article_path] = {"title": title_article,
                               "link": a_url_paper_el}

    with open(os.path.join(out_folder, "papers_ids_titles.json"), "w") as f:
        json.dump(table, f)
        
    return table

def download_pdfs(url, out_folder):
    

    table = get_papers_titles_and_ids(url, out_folder)
    
    print(f"Download papers from {url}")
    for paper_path, paper_data in tqdm(table.items()):

        if not os.path.exists(os.path.join(out_folder, paper_path)):
            try:
                response = requests.get(paper_data["link"])

                with open(os.path.join(out_folder, paper_path), 'wb') as fOut:
                    # Write content in pdf file
                    fOut.write(response.content)
            except Exception as e:
                _link = paper_data["link"]
                print(f"Fail to download {_link}")
                continue
    
            
    
    
@click.command()
@click.argument('base_url')
@click.option("--out_folder", default="conferences")
@click.option("--until", default=2010)
def main(base_url, out_folder, until):
    
    print(f"Get papers from {base_url} until year {until}")
    
    conf_base_name = base_url.rstrip("/").split("/")[-1]

    if not os.path.exists(os.path.join(out_folder, conf_base_name)):
        os.mkdir(os.path.join(out_folder, conf_base_name))
        
    years_urls = get_years_and_urls(base_url, until)

    with open(os.path.join(out_folder, conf_base_name, "years_proceedings.json"), "w") as f:
        json.dump(years_urls, f)
    
    # donwload pdfs
    for year, proceedings in years_urls.items():
        if not os.path.exists(os.path.join(out_folder, conf_base_name, year)):
            os.mkdir(os.path.join(out_folder, conf_base_name, year))
        for track_id, track in enumerate(proceedings):
            if not os.path.exists(os.path.join(out_folder, conf_base_name, year, f"track_{track_id}")):
                os.mkdir(os.path.join(out_folder, conf_base_name, year, f"track_{track_id}"))
            download_pdfs(track["link"], os.path.join(out_folder, conf_base_name, year, f"track_{track_id}"))

if __name__ == '__main__':
    main()