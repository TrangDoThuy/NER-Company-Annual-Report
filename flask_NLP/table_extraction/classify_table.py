
import re
import json
from nltk.stem import PorterStemmer
ps = PorterStemmer()


def table_classify(text):
    root = "table_extraction/"
    # root = ""
    text = text.replace("\n"," ")

    pat = re.compile(r'[^a-zA-Z ]+')
    answer = re.sub(pat, "  ", text)
    
    word_list = answer.lower().split(' ')
    word_list = list(set(word_list))

    word_list = [ps.stem(token).lower() for token in word_list]

    max_score = 0
    max_index = -1
    

    list_benchmark_file = ["operation_statement","income_statement","balance_sheet","cash_flows","equity_statement"]
    score_list = []
    for i,file in enumerate(list_benchmark_file):
        file = root + file + ".json"
        f = open(file)
        benmark_list = json.load(f)["word_list"]
        f.close()

        num_common = list(set(word_list).intersection(benmark_list))
        if len(num_common) == 0:
            score_list.append(0)
            continue
        recall = len(num_common)/len(word_list)
        precise = len(num_common)/len(benmark_list)

        f_measure = 1/(1/recall + 1/precise)

        if f_measure > max_score:
            max_score = f_measure
            max_index = i
        score_list.append(f_measure)
    if (max_score == 0):
        return -1,"others",0
    else:
        return max_index,list_benchmark_file[max_index], max_score

# f = open("test/data/content_table_0.txt", "r",encoding='utf-8')
# table_content = f.read()
# f.close()
# table_type, new_table_name, score = table_classify(table_content)
# print(table_type, new_table_name, score)
