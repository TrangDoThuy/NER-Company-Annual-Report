# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 15:04:32 2021

@author: trang
"""
import re
from boilerpy3 import extractors
import spacy
from random import seed
from random import random
import json
nlp = spacy.load("en_core_web_sm")
seed(1)

##%

def condense_newline(text):
    return '\n'.join([p for p in re.split('\n|\r', text) if len(p) > 0])

# Returns the text from a HTML file
def parse_html(html_path):
    # Text extraction with boilerpy3
    html_extractor = extractors.ArticleExtractor()
    return condense_newline(html_extractor.get_content_from_file(html_path))

# create random color
def getRandomColor(): 
    letters = '0123456789ABCDEF'
    color = '#'
    for i in range(6):
        color += letters[int(random() * 16)]
    return color

html_path = ("Data/NYSE/Agilent Technologies Inc/annual_report_2020-12-18_a-20201031.htm")
text = parse_html(html_path)
doc = nlp(text)

ent_color_dict = dict()
text_label_JSON = {}
text_label_JSON["res"]=[]

for ent in doc.ents:
    if(ent.text.isnumeric()):
        continue
    if((ent.label_ =="CARDINAL") or (ent.label == "ORDINAL")):
        continue
    # text_item = " "+ent.text+" "
    text_item = ent.text
    if(ent.label_ not in ent_color_dict):
        ent_color_dict[ent.label_] = getRandomColor()
    json_object = {}
    json_object["content"] = text_item
    json_object["tag"] = ent.label_
    json_object["color"] = ent_color_dict[ent.label_]
    text_label_JSON["res"].append(json_object)
with open('data_flask.json', 'w') as f:
    json.dump(text_label_JSON, f)

