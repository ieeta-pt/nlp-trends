

import click
import os
import re
import json
from tqdm import tqdm

import scipdf
from utils import walk_tree
from pdf_reader_text import get_all_text

@click.command()
@click.option("--folder", default="conferences")
@click.option("--update", is_flag=True)
@click.option("--progress", is_flag=True)
def main(folder, update, progress):
    
    progress = not progress
    
    pdf_failed_convertion = []
    
    total = None
    if progress:
        total = 0
        # count number of papers
        for track_path in walk_tree(folder):
            total += len(list(filter(lambda x: x.endswith(".pdf") ,os.listdir(os.path.join(track_path)))))

    print(total)
    
    with tqdm(total=total) as pBar:
        for track_path in walk_tree(folder):
     
            with open(os.path.join(track_path, "papers_ids_titles.json")) as f:
                proceedings_papers = json.load(f)
                for paper_path in filter(lambda x: x.endswith("pdf"), os.listdir(track_path)):
                    #else:
                    #    print("Warning: paper_id 1 its not a proceeding? check:",paper_title,"|id|",paper_id)
                    paper_path_name,_ = os.path.splitext(paper_path)
                    out_file_path = os.path.join(track_path, f"{paper_path_name}.json")

                    if os.path.exists(out_file_path) and not update:
                        pass
                    else:
                        try:
                            article_dict = scipdf.parse_pdf_to_dict(os.path.join(track_path, paper_path))
                            # write the changes to file
                            article_dict["full_text"] = get_all_text(os.path.join(track_path, paper_path))
                            with open(out_file_path, "w") as fOut:
                                json.dump(article_dict, fOut)
                        except Exception as e:
                            print(f"Faild to convert {os.path.join(track_path, paper_path)} to a json file. Added to the error file")
                            pdf_failed_convertion.append(os.path.join(track_path, paper_path))
                            #raise e

                    pBar.update(1)

    with open("pdf_to_json_failed_conversion.txt", "w") as f_failOut:
        for line in pdf_failed_convertion:
            f_failOut.write(f"{line}\n")
            

if __name__ == '__main__':
    main()
    #pass