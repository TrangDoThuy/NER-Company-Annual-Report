
import re
import json
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
ps = PorterStemmer()


def create_benchmark():
    json_obj = {}
    file_path = "annual_report_2021-02-16_arnc-20201231_statement of consolidated comprehensive income.html"
    with open(file_path, 'r', errors='backslashreplace') as file:
        content = file.read()

    soup = BeautifulSoup(content,"lxml")
    text = soup.text

    text = text.replace("\n"," ")

    pat = re.compile(r'[^a-zA-Z ]+')
    answer = re.sub(pat, "  ", text)
    # print(answer)

    
    word_list = answer.lower().split(' ')
    word_list = list(set(word_list))
   

    json_obj["word_list"] = [ps.stem(token).lower() for token in word_list]

    with open('income_statement.json','w',encoding='utf-8') as f:
        json.dump(json_obj, f,ensure_ascii=True, indent=4)
def trying():
    word_list = ["accumulated","other","comprehensive","number","share","retained","earn","equity","controlling","interest","additional","paid","repurchase"]
    result = [ps.stem(token).lower() for token in word_list]
    print(result)

create_benchmark()





