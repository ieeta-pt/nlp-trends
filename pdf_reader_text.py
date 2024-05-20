from PyPDF2 import PdfReader
import re
import nltk

def get_all_text(file_name):
    text = ""
    reader = PdfReader(file_name)
    for page in reader.pages:
        page_text = page.extract_text()
        #remove line breaks
        page_text = re.sub("\n", " ", page_text) 
        #remove the hyphen line breaks
        page_text = re.sub(r'(\w)-\s', r'\1', page_text)
        
        #remove page number  on the right
        index = 0

        while len(page_text)>0 and page_text[-(index+1)].isdigit():
            index+=1
        if index!=0:
            page_text = page_text[:-index]
            
        #remove page number  on the left
        index = -1
        while len(page_text)>0 and page_text[(index)+1].isdigit():
            index+=1
        if index!=-1:
            page_text = page_text[index+1:]

        text += page_text 
    
    sentences = nltk.PunktSentenceTokenizer(text).tokenize(text) 
    return sentences