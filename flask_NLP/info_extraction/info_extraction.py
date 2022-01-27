# -*- coding: utf-8 -*-
import codecs
import re
import pandas as pd
import json
import spacy
import json
from transformers import PegasusTokenizer, PegasusForConditionalGeneration, TFPegasusForConditionalGeneration

# Let's load the model and the tokenizer 
model_name = "human-centered-summarization/financial-summarization-pegasus"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name) # If you want to use the Tensorflow model 

nlp = spacy.load("en_core_web_sm")

def remove_unnecessary_letter(input_string):
    # print("--------------------------------")
    # print("===input===")
    # print(input_string)
            
    TAG_RE = re.compile(r'<[^>]+>')
    TABLE_CONTENT_RE = re.compile(r'[0-9]+\s+Table of Contents')
    TABLE_CONTENT_RE_2 = re.compile(r'[0-9]\(table of contents\)')
    TABLE_CONTENT_RE_3 = re.compile(r'[0-9]+Table of Contents')
    SPACE_RE = re.compile(r'(\s\s)+')
    

    list_remove_re = [TABLE_CONTENT_RE,SPACE_RE,TABLE_CONTENT_RE_2,TABLE_CONTENT_RE_3]
    input_string = re.sub(TAG_RE," ", input_string)
    for remove_re in list_remove_re:
        input_string = re.sub(remove_re,' ', input_string)
        
    input_string = input_string.replace('.\n',"hihi")
    
    remove_items = ["&nbsp;","&nbsp","nbsp;","nbsp","   ","\n"] 
    for item in remove_items:
        input_string = input_string.replace(item," ")
    input_string = input_string.replace("tem&#160;","tem ")
    input_string = input_string.replace("&middot;","\n\t &middot;")
    input_string = input_string.replace("hihi",'.\n')
    input_string = input_string.replace("haha",' ')
    input_string = input_string.replace("\n\n",'\n')
    # input_string = input_string.replace(" .",'.')
    input_string = input_string.replace(" ,",',')
    input_string = input_string.strip() 

    # print("====return====")
    # print(input_string)
    
    return input_string

def extract_item_1_business(file_path):
    
    f=codecs.open(file_path, 'r')
    file_content = f.read()
    f.close()
    #regex = re.compile(r'(>ITEM[^1]+1)|(>Item[^1]+1)')
    # regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>Item(1A|2|1.)\.{0,1})|(>(\s)+Item(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>(\s)+Item(1A|2|1.)\.{0,1})|(>ITEM(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>ITEM(1A|2|1.)\.{0,1})|(>(\s)+ITEM(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>(\s)+ITEM(1A|2|1.)\.{0,1})|(>ITEM[^<]+<)|(>Item[^<]+<)|(>ITEM[^2]+2.)|(>Item[^2]+2.)|(>ITEM[^1]+1.)|(>Item[^1]+1.)|(>ITEM[^1]+1A.)|(>Item[^1]+1A.)|(>Item </a>1)|(>Item </a>1A.)|(>Item[^\.]+\.)')
    regex = re.compile(r'(>Item[^&f]+(&|f))|(>Item(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>Item(1A|2|1.)\.{0,1})|(>(\s)+Item(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>(\s)+Item(1A|2|1.)\.{0,1})|(>ITEM(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>ITEM(1A|2|1.)\.{0,1})|(>(\s)+ITEM(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>(\s)+ITEM(1A|2|1.)\.{0,1})|(>ITEM[^2]+2.)|(>Item[^2]+2.)|(>ITEM[^1]+1.)|(>Item[^1]+1.)|(>ITEM[^1]+1A.)|(>Item[^1]+1A.)|(>Item </a>1)|(>Item </a>1A.)')
    
    matches = regex.finditer(file_content)
    item_1_raw = ""
    # Create the dataframe
    if(len(list(matches))>0):
        matches = regex.finditer(file_content)
        test_df = pd.DataFrame(columns=[ 'start', 'end','header'])
        data = []
        for match in matches:

            
            header = file_content[match.start()+1:match.end()]

            # start_remove = header.find('<')
            header = remove_unnecessary_letter(header).lower()  
            regex = re.compile('[^a-zA-Z0-9\s]')
            #First parameter is the replacement, second parameter is your input string
            header = regex.sub('', header)
            header = header.replace("  "," ")
            header = header.replace("f","")
            # print(header+"//")
            # print("--------")
            
            # if (header not in ["item 1","item 1a","item 2"]):
            #     continue
            if ("item 1 " in header) or (header == "item 1"):
                header = "item 1"
            elif ("item 1a " in header) or (header == "item 1a"):
                header = "item 1a"
            elif ("item 2 " in header) or (header == "item 2"):
                header = "item 2"
            else: 
                continue
            new_row = {'start':match.start()+1,'end':match.end(),'header':header}
            data.append(new_row)
        test_df = pd.DataFrame(data)
        # print(test_df)
        
        start1 = 0
        end1 = 0
        max_len = 0

        for i in range(len(test_df)-1):
            length = test_df.iloc[i+1]['start'] - test_df.iloc[i]['start']
            if(test_df.iloc[i]['header'] == "item 1"):
                if length > max_len:
                    max_len = length
                    start1 = test_df.iloc[i]['start']
                    end1 = test_df.iloc[i+1]['start']
                
        item_1_raw = file_content[start1:end1]
        # remove unnecessary break line:
        item_1_raw = item_1_raw.replace('.\n',"hihi")
        item_1_raw = item_1_raw.replace('\n'," ")
        item_1_raw = item_1_raw.replace("hihi",'.\n')
    return item_1_raw

def extract_item_7_financial_analyse(file_path):
    f=codecs.open(file_path, 'r')
    file_content = f.read()
    f.close()
    regex = re.compile(r'(>Item[^&f]+(&|f))|(>Item(\s|&#160;|&nbsp;)(7A|8|7.)\.{0,1})|(>Item(7A|8|7.)\.{0,1})|(>(\s)+Item(\s|&#160;|&nbsp;)(7A|8|7.)\.{0,1})|(>(\s)+Item(7A|8|7.)\.{0,1})|(>ITEM(\s|&#160;|&nbsp;)(7A|8|7.)\.{0,1})|(>ITEM(7A|8|7.)\.{0,1})|(>(\s)+ITEM(\s|&#160;|&nbsp;)(7A|8|7.)\.{0,1})|(>(\s)+ITEM(7A|8|7.)\.{0,1})|(>ITEM[^<]+<)|(>Item[^<]+<)|(>7. MANAGEMENT)')
    # regex = re.compile(r'(>Item[^&f]+(&|f))|(>Item(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>Item(1A|2|1.)\.{0,1})|(>(\s)+Item(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>(\s)+Item(1A|2|1.)\.{0,1})|(>ITEM(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>ITEM(1A|2|1.)\.{0,1})|(>(\s)+ITEM(\s|&#160;|&nbsp;)(1A|2|1.)\.{0,1})|(>(\s)+ITEM(1A|2|1.)\.{0,1})|(>ITEM[^2]+2.)|(>Item[^2]+2.)|(>ITEM[^1]+1.)|(>Item[^1]+1.)|(>ITEM[^1]+1A.)|(>Item[^1]+1A.)|(>Item </a>1)|(>Item </a>1A.)')

    matches = regex.finditer(file_content)
    item_7_raw = ""
    # Create the dataframe
    if(len(list(matches))>0):
        matches = regex.finditer(file_content)
        test_df = pd.DataFrame(columns=[ 'start', 'end','header'])
        data = []
        for match in matches:
            
            
            header = file_content[match.start()+1:match.end()]

            header = remove_unnecessary_letter(header).lower()
            regex = re.compile('[^a-zA-Z0-9\s]')
            #First parameter is the replacement, second parameter is your input string
            header = regex.sub('', header)
            header = header.replace("  "," ")
            # print("---------")
            # print(header+"//")
            # if header == "7 management":
            #     header = "item 7"
            if ("item 7 " in header) or (header == "item 7"):
                header = "item 7"
            elif ("item 7a " in header) or (header == "item 7a"):
                header = "item 7a"
            elif ("item 8 " in header) or (header == "item 8"):
                header = "item 8"
            elif "7 management" in header:
                header = "item 7"
            else: 
                continue
            
            if (header not in ["item 7","item 7a","item 8"]):
                continue
            new_row = {'start':match.start()+1,'end':match.end(),'header':header}
            data.append(new_row)
        test_df = pd.DataFrame(data)
        # print(test_df)
        
        start7 = 0
        end7 = 0
        max_len = 0

        for i in range(len(test_df)-1):
            length = test_df.iloc[i+1]['start'] - test_df.iloc[i]['start']
            if(test_df.iloc[i]['header'] == "item 7"):
                if length > max_len:
                    max_len = length
                    start7 = test_df.iloc[i]['start']
                    end7 = test_df.iloc[i+1]['start']
        item_7_raw = file_content[start7:end7]

        # remove uncenessary break line:
        item_7_raw = item_7_raw.replace('.\n',"hihi")
        item_7_raw = item_7_raw.replace('\n'," ")
        item_7_raw = item_7_raw.replace("hihi",'.\n')
    return item_7_raw

def generate_header_content(raw_text):
    while "<TABLE" in raw_text:
        start_index = raw_text.index("<TABLE")
        if "</TABLE>" in raw_text[start_index:]:
            end_index = raw_text.index("</TABLE>",start_index) 
            raw_text = raw_text.replace(raw_text[start_index:(end_index+8)],' ')
        else:
            break
        
    while "<table" in raw_text:
        start_index = raw_text.index("<table")
        if "</table>" in raw_text[start_index:]:
            end_index = raw_text.index("</table>",start_index)
            raw_text = raw_text.replace(raw_text[start_index:(end_index+8)],' ')
        else:
            break

    raw_text = raw_text.replace(".\n",". ")
    raw_text = raw_text.replace("\n","")
    
    
    # Write the regex
    regex = re.compile(r'(<B><U>[^<]+</U></B>)|(<B><I>[^<]+</I></B>)|(<B>[^/]+</)|(<b>[^/]+</)|(<b><u>[^/]+</u></b>)|(<b><i>[^/]+</i></b>)|(bold[^<]+</)|(font-weight:700[^<]+</)|(font-weight: 700[^<]+</)')
    # Use finditer to math the regex
    matches = regex.finditer(raw_text)
    # Create the dataframe
    data = []
    test_df = pd.DataFrame(columns=[ 'start', 'end','header'])
    
    for match in matches:
        # print(match)
        start_index = raw_text.index('>',match.start(),match.end())+1
        end_index = raw_text.index('</',start_index,match.end())
        header = raw_text[start_index:end_index]
        header = remove_unnecessary_letter(header).lower()
        new_row = {'start':start_index,'end':end_index,'header':header}
        data.append(new_row)
    test_df = pd.DataFrame(data)
    # print (test_df)
    
    list_content =[]
    for i in range(1, len(test_df["start"])):
        content = raw_text[test_df.end[i-1]:test_df.start[i]]
        list_content.append(content)
        # print(content)
        # print("------")
    list_content.append(raw_text[test_df.end[len(test_df.end)-1]:len(raw_text)])
    test_df["content"] = list_content
    # first json object
    first_part = raw_text[:test_df.iloc[0]['start']]
    title = first_part[:(first_part.index('</'))]
    title = remove_unnecessary_letter(title)
    body = first_part[(first_part.index('</')):]
    if("<P>" in body):
        body = body[:(body.index('<P>'))]
    body = remove_unnecessary_letter(body)
    object_list = []
    json_object = {}
    json_object["header"] = title
    json_object["content"] = body
    object_list.append(json_object)

    for index, row in test_df.iterrows():
        json_object = {}
        json_object["header"] = remove_unnecessary_letter(row['header'])
        json_object["content"] = remove_unnecessary_letter(row['content'])

        object_list.append(json_object)

    return object_list

def extract_overview_and_business_review(object_list):
    # extract business review:
    
    has_business_review_title = False
    for i in range(1,len(object_list)):
        
        if (("business" in object_list[i]["header"].lower()) and (len(object_list[i]["header"].lower())>10)):
            has_business_review_title = True
            if(len(object_list[i]["content"])>0):
                business_review = object_list[i]["content"]
                break
            else:
                business_review = object_list[i+1]["content"]
                break
    common_title =["our company","the company","overview"]
    not_true_title = ["industry overview"]
    checking = True
    has_overview_title = False
    for i in range(len(object_list)):
        if (not checking):
            break
        if any(title in object_list[i]["header"].lower() for title in not_true_title):
            continue
        for title in common_title:
            if title in object_list[i]["header"].lower():            
                has_overview_title = True
                while((i<len(object_list))and(len(object_list[i]["content"])==0)):
                    i +=1
                overview = object_list[i]["content"]
                if(not has_business_review_title):
                    i +=1
                    while((i<len(object_list))and(len(object_list[i]["content"])==0)):
                        i +=1
                    business_review =  object_list[i]["content"]  
                checking = False
                break

    if(not has_overview_title):
        i = 0
        while((i<len(object_list)-1) and len(object_list[i]["content"])==0):
            i +=1
        overview = object_list[i]["content"]
        i +=1
        while((i<len(object_list)-1) and len(object_list[i]["content"])==0):
            i +=1
        business_review =  object_list[i]["content"] 
    return overview,business_review

def performance_extraction(object_list):
    nlp = spacy.load("en_core_web_sm")
    max_ratio = 0
    performance = ""
    for item in object_list:
        content = item['content']
        if(len(content)==0):
            continue
        paragraphs = content.split("\n")
        for paragraph in paragraphs:
            if(len(paragraph)<5):
                continue                
            doc = nlp(paragraph)
            count_money = 0
            count_date = 0
            count_revenue_income = 0
            for ent in doc.ents:
                if(ent.label_=="MONEY"):
                    count_money+=1
                if(ent.label_ == "DATE"):
                    count_date+=1
            count_revenue_income += paragraph.lower().count('revenue')
            count_revenue_income += paragraph.lower().count('income')
            count_revenue_income -= paragraph.lower().count('fee')
            count_revenue_income -= paragraph.lower().count('expenses')
            count_revenue_income -= paragraph.lower().count('tax')
            ratio = (count_money*count_date*count_revenue_income)/len(paragraph)
            if(ratio>max_ratio):
                performance = paragraph
                max_ratio = ratio
    return performance

def replace_func(paragraph):

    map_quotes = [{
        "long_name":"&rsquo;",
        "short_name":"\'",
    },
    { "long_name":"&#146;",
        "short_name":"\'",
    },
    {
        "long_name":"&ldquo;",
        "short_name":"\"",
    },
    {
        "long_name":"&rdquo;",
        "short_name":"\"",
    },
    {
        "long_name":"&#8220;",
        "short_name":"\"",
    },
    {
        "long_name":"&#8221;",
        "short_name":"\"",
    },
    {
        "long_name":"&#147;",
        "short_name":"\"",
    },
    {
        "long_name":"&#148;",
        "short_name":"\"",
    },
    {
        "long_name":"&ndash;",
        "short_name":"–",
    },
    {
        "long_name":"&amp;",
        "short_name":"&",
    },
    {
        "long_name":"&mdash;",
        "short_name":"—",
    },
    {
        "long_name":"&#160;",
        "short_name":" ",
    },
    {
        "long_name":"&#8217;",
        "short_name":"’",
    },
    {
        "long_name":"&#8226;",
        "short_name":"\n •",
    },
    ]
    for quote in map_quotes:
        paragraph = paragraph.replace(quote["long_name"],quote["short_name"])

    return paragraph

def fine_tune_paragraph(paragraph):

    paragraph = paragraph.replace("  "," ").replace(". ",".. ")
    paragraph = paragraph.replace(".\n",".. ")
    paragraph = paragraph.replace("\n",". ")
    sentence_list = paragraph.split(". ")
    
    return sentence_list   

def get_subject_phrase(doc):
    for token in doc:
        if ("subj" in token.dep_):
            subtree = list(token.subtree)
            start = subtree[0].i
            end = subtree[-1].i + 1
            return doc[start:end]

def prospects_extraction(object_list):
    future_word_list = ["anticipates","believes","feels","expects","estimates","seeks","strives","plans","intends",
                        "outlook","forecast","position","target","mission","assume","achievable","potential",
                        "strategy","goal","aspiration","outcome","continue","remain","maintain",
                        "trend","objective","will ","would","should","could","might"," can ","may"]

    current_count = 0
    max_count = 0
    prospects_paragraph = []
    for item in object_list:
        content = item['content']
        if(len(content)==0):
            continue
        paragraphs = content.split("\n")
        for paragraph in paragraphs:
            if(("forward-looking statements" in paragraph)):
                continue
            doc = nlp(paragraph)
            sentences = list(doc.sents)
            for i in range(len(sentences)):
                sentence = sentences[i]
                
                subject_phrase = get_subject_phrase(nlp(sentence.text))
                if(str(subject_phrase).lower() not in ["we","the company"]):
                    continue
                elif(("will be" in sentence.text)or("if" in sentence.text)):
                    continue
                current_count = 0
                current_word_list=[]
                for word in future_word_list:
                    current_count += sentence.text.count(word)
                    if(sentence.text.count(word)>0):
                        current_word_list.append(word)
                if(current_count > max_count):
                    max_count = current_count
                    if((("their" in sentence.text)or("such" in sentence.text))and(i>0)):
                        sentence_content = sentences[i-1].text +" "+  sentence.text
                    else:
                        sentence_content = sentence.text
                    prospects_paragraph.append(sentence_content)
    return prospects_paragraph 

def fine_tune_sents(paragraph):
    doc = nlp(paragraph)
    new_paragraph = ""
    for sent in doc.sents:
        if sent[0].is_title and sent[-1].is_punct:
            has_noun = 2
            has_verb = 1
            for token in sent:
                if token.pos_ in ["NOUN", "PROPN", "PRON"]:
                    has_noun -= 1
                elif token.pos_ == "VERB":
                    has_verb -= 1
            if has_noun < 1 and has_verb < 1:
                added_sent = str(sent) + "\n "
                new_paragraph += added_sent
    if len(new_paragraph)<10:
        return paragraph
    return new_paragraph

def summary(paragraph):

    # divide paragraph into more chunk with 2000 length for each
    list_chunk = []
    
    while len(paragraph)>2000:
        index = paragraph.find(". ", 2000)
        list_chunk.append(paragraph[:index+1])
        paragraph = paragraph[index+1:]
    list_chunk.append(paragraph)
    summary_para = ""

    for para in list_chunk:
        # Tokenize our text
        # If you want to run the code in Tensorflow, please remember to return the particular tensors as simply as using return_tensors = 'tf'
        input_ids = tokenizer(para, return_tensors="pt").input_ids
        # Generate the output (Here, we use beam search but you can also use any other strategy you like)
        output = model.generate(
            input_ids, 
            max_length=1000, 
            num_beams=5, 
            early_stopping=True
        )
        sum_sent = tokenizer.decode(output[0], skip_special_tokens=True)
        sum_sent = sum_sent+"\n"
        summary_para += sum_sent

    new_para = fine_tune_sents(summary_para)

    return(new_para)

def model_info_extraction(file_path):
    # print("------file path----------")
    # print(file_path)
    raw_text_item_1 = extract_item_1_business(file_path)
    # f = open("sample_raw_1_2020.txt", "w")
    # f.write(raw_text_item_1)
    # f.close()
    #  raw_text_item_1 still correct

    object_list_item_1 = generate_header_content(raw_text_item_1)
    # with open('sample_list_item_1.json', 'w', encoding='utf-8') as f:
    #     json.dump(object_list_item_1, f, ensure_ascii=False, indent=4)


    # # error in object_list_item_1
    overview, business_review =  extract_overview_and_business_review(object_list_item_1)

    non_list_obj = {}
    list_obj = {}
    non_list_obj["Summary"] = {}

    overview = replace_func(overview)
    non_list_obj["Overview"] = overview
    non_list_obj["Summary"]["Overview"] = summary(overview)
    # print("============overview========")
    # print(overview)
    overview = fine_tune_paragraph(overview)
    # overview_list = overview.split(". ")
    list_obj["overview"] = overview

    business_review = replace_func(business_review)
    non_list_obj["Business Review"] = business_review
    non_list_obj["Summary"]["Business Review"] = summary(business_review)
    business_review = fine_tune_paragraph(business_review)
    # business_review = business_review.split(". ")
    list_obj["business_review"] = business_review

    raw_text_item_7 = extract_item_7_financial_analyse(file_path)
    # f = open("sample_raw_7_2010_09.txt", "w")
    # f.write(raw_text_item_7)
    # f.close()

    object_list_item_7 = generate_header_content(raw_text_item_7)
    # with open('sample_list_item_7.json', 'w', encoding='utf-8') as f:
    #     json.dump(object_list_item_7, f, ensure_ascii=False, indent=4)


    performance = performance_extraction(object_list_item_7)   
    performance = replace_func(performance)
    # print(performance)
    non_list_obj["Performance"] = performance
    # print("============")
    # print(len(performance))
    # print("----------------------")
    # print(performance)
    non_list_obj["Summary"]["Performance"] = summary(performance) 
    # performance = performance.split(". ")
    performance = fine_tune_paragraph(performance)
    list_obj["performance"] = performance

    prospect_paragraph = ""
    for item in prospects_extraction(object_list_item_7):
        prospect_paragraph = prospect_paragraph+item+" \n"
    
    prospect_paragraph = replace_func(prospect_paragraph)
    non_list_obj["Prospects"] = prospect_paragraph
    non_list_obj["Summary"]["Prospects"] = summary(prospect_paragraph)
    # prospect_paragraph = prospect_paragraph.split(". ")
    prospect_paragraph = fine_tune_paragraph(prospect_paragraph)
    list_obj["prospects"] = prospect_paragraph

    return list_obj,non_list_obj 

# file_path = 'test/data/annual_report_2020-12-18_a-20201031.htm' 
# model_info_extraction(file_path)  
