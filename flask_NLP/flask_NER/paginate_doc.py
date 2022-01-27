# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 12:27:49 2021

@author: trang
"""

from bs4 import BeautifulSoup
import re

def paginate_doc(file_directory):

# file_directory = "static/Data/OTC/Avantair Inc/annual_report_2007-12-05_d10ka.htm"

    soup = BeautifulSoup(open(file_directory, 'r'), 'html.parser')
    text = soup.find('text')
    if text != None:
        document = str(text)
        children_count = len(text.contents)
        # print(document[:1000])
        # print(document[-1000:])
    else:
        body = soup.body
        body = soup.find('body')
        children_count = len(body.contents)
        while(children_count == 1):         
            body = body.contents[0]
            children_count = len(body.contents)
        document = str(body)

    if(document.find("pagination__item")== -1):
        # <title>a-20201031</title></head><body>
        start_body = document.find("<body")
        start_body_index = document.find(">",start_body)+1
        # </body></html>
        end_body_index = document.find("</body>",start_body_index )
        if(document.find("pagination__list")== -1):
            if(children_count>1):
                # add whole div for pagination
                whole_div = "<div id=\"pagination-1\" class=\"pagination__list\"><div class=\"pagination__item\">"
                document = document[:start_body_index]+ whole_div +document[start_body_index:end_body_index]+"</div></div></body>"
            else:
                sub_start = document.find(">",start_body_index)+1
                whole_div = "<div id=\"pagination-1\" class=\"pagination__list\"><div class=\"pagination__item\">"
                document = document[:sub_start]+ whole_div +document[sub_start:end_body_index]+"</div></div></body>"
        
        # replace horizontal line by page-break
        regex = re.compile(r'<hr[^>]+>')
        matches = list(regex.finditer(document))
        replace_paginate = "</div><div class=\"pagination__item\">"
        break_page_list = ["<!-- Field: /Page -->","<div id=\"PGBRK\" style=\"MARGIN-LEFT: 0pt; TEXT-INDENT: 0pt; MARGIN-RIGHT: 0pt\">"]
        if len(matches)>0:
            for match in matches:
                break_page = document[match.start():match.end()]
                if break_page not in break_page_list:
                    break_page_list.append(break_page)
                    
        for break_page in break_page_list:
            if "width=\"17%\"" in break_page:
                continue
            document = document.replace(break_page,replace_paginate)

    return document

# file_directory = "static/Data/OTC/Avantair Inc/annual_report_2008-09-24_v127155_10k.htm"
# document = paginate_doc(file_directory)
# Html_file= open("trying_HTML.html","w", encoding="utf-8")
# Html_file.write(document)
# Html_file.close()
