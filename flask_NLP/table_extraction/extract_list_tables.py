from bs4 import BeautifulSoup
import json
import pandas as pd
from table_extraction.classify_table import table_classify
# from classify_table import table_classify

def check_quantitative_table(table):
    if len(str(table)) > 1000:
        content = table.text
        if ("10-Q" in content) or ("8-K" in content) or ("10-K" in content) or ("page" in content.lower()):
            return False,0

        numbers = sum(n.isdigit() for n in content)
        letters = sum(c.isalpha() for c in content)
        if numbers*10> letters:
            return True
    return False

def extract_list_tables(file_path):
    try:
        with open(file_path, 'r', errors='backslashreplace') as file:
            content = file.read()
    except:
        return None

    soup = BeautifulSoup(content,"lxml")

    tables = soup.findAll("table")
    tables_json = {}
    tables_json["table"] = []

    max_score_table_type = [{"score":0,"name":"","content":""} for _ in range(6)]

    for table in tables:

        quant = check_quantitative_table(table)

        if quant == True:
            content_table = table.text
            table_type, new_table_name, score = table_classify(content_table)
            if table_type != -1:
                max_score = max_score_table_type[table_type]["score"]
                if score > max_score:
                    max_score_table_type[table_type] = {"name":new_table_name ,"score":score,"content":str(table)}
    
    for i in range(6):
        table_obj={}
        table_obj["name"] = max_score_table_type[i]["name"]
        table_obj["content"] = max_score_table_type[i]["content"]
        table_obj["category"] = i+1
        table_obj["score"] = max_score_table_type[i]["score"]
        tables_json["table"].append(table_obj)

    # with open('new_tables_json.json','w',encoding='utf-8') as f:
    #     json.dump(tables_json, f,ensure_ascii=True, indent=4)

    return tables_json

def extract_table(file_path):
    tables_json = extract_list_tables(file_path)
    list_file_path = []

    empty_table = 0
    for table in tables_json["table"]:
        if len(table["content"])<10:
            empty_table += 1
        if empty_table >= 2:
            return []

    for table in tables_json["table"]:
        table_type = table["category"]
        if len(table["content"])<10:
            continue

        file_name_html = file_path.split(".")[0]+"_"+table["name"]+".html"
        with open(file_name_html, "w", encoding='utf-8') as file:
            file.write(table["content"])
        table_html_obj = {
            "category": table_type,
            "file_directory": file_name_html,
            "file_type": "html"
        }
        list_file_path.append(table_html_obj)

        file_name_json = file_path.split(".")[0]+"_"+table["name"]+".json"
        tables_df =pd.read_html(table["content"])
        table_json = tables_df[0].to_json(orient="split")
        with open(file_name_json,'w',encoding='utf-8') as f:
            json.dump(table_json, f,ensure_ascii=True, indent=4)        
        table_json_obj = {
            "category":table_type,
            "file_directory":file_name_json,
            "file_type":"json"
        }
        list_file_path.append(table_json_obj)
    # with open('list_file_path.json','w',encoding='utf-8') as f:
    #     json.dump(list_file_path, f,ensure_ascii=True, indent=4)
    return list_file_path

# file_path = "test/data/annual_report_2008-12-19_a2189713z10-k.htm"
# extract_table(file_path)