# Trends in Natural Language Processing

This repository depicts the code used for our analysis of Natural Language Processing as presented in the work:

"Analyzing a Decade of Evolution: Trends in Natural Language Processing"

## Setup 

The necessary `requirements.txt` file is provided for the necessary python depnedancies.

## Dataset Pre-Processing

The dataset containing the various corpora is provided on [Zenodo}(https://zenodo.org/records/11222088), alternatively users can run our pipeline to create the corpus:

1. **Download papers**: In order to download the necessary papers used in this work, we provide the `download_from_acl.sh` bash script.
2. **Parse PDF**: In order to convert the PDFs into human readable text, we provide the `pdf_to_json.py` file which converts the PDFs to parsed JSON representation.

## Data Extraction

In order to extract the various GPU information, we provide the `gpu_extraction_1.py` file, which will create some of the files present in the `output` directory, using the JSON representations presented above.

We also proved our script used to query ChatGPT, however this is likely outdated due to changes in API `openai.py`.

Finally we also provide code to query citation information for the papers in both `paper_citations_from_scholar.py` and `paper_citations_from_semantic.py`.


