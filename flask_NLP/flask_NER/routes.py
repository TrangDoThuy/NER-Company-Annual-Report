from flask import render_template, request, jsonify
from flask_NER import app,db
from flask_NER.models import Company, Report,Exchange,JSON_file,JSON_type, table_file, table_type
from doc_pagination.paginate_doc import paginate_doc
from table_extraction.extract_list_tables import extract_table
import codecs
import json
import re
import spacy
import colorsys
nlp = spacy.load("en_core_web_sm")
import ahocorasick
from bs4 import BeautifulSoup
A = ahocorasick.Automaton()
from info_extraction.info_extraction import model_info_extraction
from model_NER.use_BERT_model import use_BERT_model
import sys
sys.setrecursionlimit(10000)

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page',1,type=int)
    companies = Company.query.order_by(Company.id).paginate(page = page, per_page = 20)
    exchanges = Exchange.query.order_by(Exchange.exchange_name)
    return render_template('home.html',companies = companies, exchanges = exchanges,currentExchangeId=0)

@app.route("/exchange/<int:exchangeId>")
def exchange(exchangeId):
    page = request.args.get('page',1,type=int)
    if(exchangeId == 0):
        companies = Company.query.order_by(Company.id).paginate(page = page, per_page = 20)
    else:
        companies = Company.query.filter_by(exchangeId=exchangeId).order_by(Company.id).paginate(page = page, per_page = 20)
    exchanges = Exchange.query.order_by(Exchange.exchange_name)
    return render_template('home.html',companies = companies, exchanges = exchanges,currentExchangeId= exchangeId)   

@app.route("/company/<int:company_id>")
def company_reports(company_id):
    page = request.args.get('page',1,type=int)
    company = Company.query.filter_by(id=company_id).first_or_404()
    reports = Report.query.filter_by(companyId=company_id).paginate(page = page,per_page=20)

    return render_template('company_reports.html',reports=reports,company=company)


@app.route("/update", methods=['POST'])
def update():
    if request.method == 'POST':
        data = eval(request.form["data"])
    return jsonify({"status": True, "data":data })


@app.route("/confirm_extraction", methods=['POST'])
def confirm_extraction():
    if request.method == 'POST':
        data = eval(request.form["data"])
    return jsonify({"status": True, "data":data })

@app.route("/NER/<int:report_id>", methods=['GET' ])
def NER(report_id):
    
    report = Report.query.filter_by(id=report_id).first_or_404()
    original_file = 'flask_NER/static/'+report.file_directory
    # if doesnt have splitted HTML, do split the original file
    splitted_HTML_num = JSON_file.query.filter_by(original_fileID=report_id,category=5).count()
    if splitted_HTML_num != 0:
        splitted_HTML = JSON_file.query.filter_by(original_fileID=report_id,category=5).first_or_404()
        splitted_HTML_dir = splitted_HTML.file_directory
        f=codecs.open(splitted_HTML_dir, 'r',encoding="utf-8")
        # print("=======splited=========")
        # print(splitted_HTML_dir)
        data= f.read()
        return render_template('NER.html',report=report, original_file=original_file,data=data,type='NER')
    else:       
        data = paginate_doc(original_file)
        # Create splitted HTML file
        file_directory = original_file.split(".")[0]+"_splitted_HTML.html"
        with open(file_directory, 'w',encoding="utf-8") as f:
            f.write(data)
        #store the file directory to database 
        new_file =  JSON_file(original_fileID=report_id,file_directory=file_directory,category=5)
        db.session.add(new_file)
        db.session.commit()
        return render_template('NER.html',report=report, original_file=original_file,data=data,type='NER')

@app.route("/table_extraction/<int:report_id>", methods=['GET' ])
def table_extraction(report_id):

    class Table:
        def __init__(self, name, link, content):
            self.name = name
            self.link = link
            self.content = content

    report = Report.query.filter_by(id=report_id).first_or_404()
    company_id = report.companyId
    company = Company.query.filter_by(id=company_id).first_or_404()

    table_file_num = table_file.query.filter_by(report_id=report_id).count()
    if table_file_num == 0:
        file_dir = 'flask_NER/static/' + report.file_directory
        list_file_path = extract_table(file_path = file_dir)
        for file in list_file_path:
            new_file = table_file(report_id = report_id, file_directory = file["file_directory"], category = file["category"], file_type = file["file_type"])
            db.session.add(new_file)
        db.session.commit()

    tables = []

    for i in range(1,7):
        type = table_type.query.filter_by(id=i).first_or_404()
        table_name = type.type_name
        table_link = "#"+table_name


        table_num = table_file.query.filter_by(report_id=report_id,category=i,file_type="html").count()
        if table_num == 0:
            table_content = """<div style="color:gray; text-align: center">Data is not available</div>"""

        else:
            table = table_file.query.filter_by(report_id=report_id,category=i,file_type="html").first_or_404()        
            f=codecs.open(table.file_directory, 'r',encoding="utf-8")
            table_content = f.read()

        table_obj = Table(table_name, table_link, table_content)
        tables.append(table_obj)

    return render_template('table_extraction.html', report = report, company = company, tables = tables, data="""<div>Data is not available</div>""")
    
# doing
@app.route("/summary/<int:report_id>", methods=['GET'])
def summary(report_id):
    class Paragraph:
        def __init__(self,title,link,id,content):
            self.title = title
            self.link = link
            self.content = content
            self.id = id
    class Sentence:
        def __init__(self,title,content):
            self.title = title
            self.content = content



    report = Report.query.filter_by(id=report_id).first_or_404()
    date = report.report_period
    company_id = report.companyId
    company = Company.query.filter_by(id=company_id).first_or_404()
    file_dir = 'flask_NER/static/' + report.file_directory

    summary_file_no = JSON_file.query.filter_by(original_fileID=report_id,category=6).count()
    if summary_file_no != 0:
        summary_file = JSON_file.query.filter_by(original_fileID=report_id,category=6).first_or_404()
        summary_file_dir = summary_file.file_directory

        f = open(summary_file_dir)
        data = json.load(f)
    else:
        _,data = model_info_extraction(file_dir)

    paras = []
    sents = []

    for item in data:
        if str(item) == "Summary":
            for sum_item in data[item]:
                data[item][sum_item] = data[item][sum_item].replace("\n","<br/>")
                sent_obj = Sentence(sum_item,data[item][sum_item])
                sents.append(sent_obj)
        else:
            if len(data[item])<3:
                data[item] = "Data is not available"
            para_id = item[:3]
            para_link = "#"+ para_id
            data[item] = data[item].replace("\n •","<br/>     •")
            para_obj = Paragraph(item,para_link,para_id,data[item])
            paras.append(para_obj)

    # save json summary file for the first time
    if summary_file_no == 0:
        folder_dir = file_dir.split(".")[0]
        summary_file = folder_dir+"_summary.json"
        json_object = json.dumps(data,indent=4)
        with open(summary_file,"w") as outfile:
            outfile.write(json_object)

        json_file = JSON_file(original_fileID=report_id,file_directory=summary_file,category=6)
        db.session.add(json_file)
        db.session.commit()

    return render_template('summary.html', report = report ,company = company, paras = paras, sents = sents, date = date)

@app.route("/confirm_NER",methods=['POST'])
def confirm_NER():
    if request.method == 'POST':
        data = eval(request.form["data"])
        # print(data)
        # create json file
        original_file = data["original_file"].strip()
        report_id = data["report_id"]
        folder_dir = original_file.split(".")[0]
        file_directory = folder_dir+"_latest_NER.json"
        json_object = json.dumps(data,indent=4)
        with open(file_directory,"w") as outfile:
            outfile.write(json_object)
        # store the file directory to database
        json_file_num = JSON_file.query.filter_by(original_fileID=report_id,category=2).count()
        if json_file_num == 0:
            json_file = JSON_file(original_fileID=report_id,file_directory=file_directory,category=2)
            db.session.add(json_file)
        else:
            json_file = JSON_file.query.filter_by(original_fileID=report_id,category=2).first_or_404()
            json_file.file_directory = file_directory
        db.session.commit()
    return jsonify({"status": True, "data":data })

@app.route("/get_latest_NER",methods=["POST"])
def get_latest_NER():
    if request.method == 'POST':
        data = eval(request.form['data'])
        report_id = data['report_id']
        # if doesnt have latest, return the original file 
        json_file_num = JSON_file.query.filter_by(original_fileID=report_id,category=2).count()
        if json_file_num != 0:
            json_file = JSON_file.query.filter_by(original_fileID=report_id,category=2).first_or_404()
            file_directory = json_file.file_directory
            f = open(file_directory)
            data = json.load(f)
            return jsonify({"status": True, "data":data })
    return jsonify({"status": False })

@app.route("/get_original_NER",methods=["POST"])
def get_original_NER():
   
    if request.method == 'POST':
        data = eval(request.form['data'])
        content_page = data['content']

        doc = nlp(content_page)
        f = open('flask_NER/static/SpaCy_util/tag2name_color.json')
        tag2name_color = json.load(f)
        f.close()

        text_label_JSON = {}
        text_label_JSON["res"]=[]

        for ent in doc.ents:
            if(ent.text.isnumeric()):
                continue
            if((ent.label_ =="CARDINAL") or (ent.label_ == "ORDINAL")):
                continue

            text_item = ent.text
            json_object = {}
            json_object["content"] = text_item
            json_object["tag"] = tag2name_color[ent.label_]["name"]    
            json_object["color"] = tag2name_color[ent.label_]["color"]
            text_label_JSON["res"].append(json_object)

        data = text_label_JSON
        return jsonify({"status": True, "data":data })
    return jsonify({"status": False })   

@app.route("/get_original_ML_NER",methods=["POST"])
def get_original_ML_NER():

    if request.method == 'POST':
        data = eval(request.form['data'])
        content_page = data['content']
        f = open("sample_input_use_BERT_model.txt", "w", encoding='utf-8')
        f.write(content_page)
        f.close()
        data = use_BERT_model(content_page)

        return jsonify({"status":True,"data":data})

    return jsonify({"status": False})

@app.route("/info_extraction/<int:report_id>")
def info_extraction(report_id):
    report = Report.query.filter_by(id=report_id).first_or_404()
    original_file = 'flask_NER/static/'+report.file_directory

    soup = BeautifulSoup(open(original_file, 'r'), 'html.parser')
    body = soup.body
    body = soup.find('body')
    children_count = len(body.contents)

    while(children_count == 1):
        body = body.contents[0]
        children_count = len(body.contents)
    data = str(body)

    def paginate_document(document,children_count):

        if(document.find("pagination__item")== -1):
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
            break_page_list = ["<hr style=\"page-break-after: always\" />","<hr style=\"page-break-after:always\"/>","<hr style=\"page-break-after:always\"></hr>","<hr noshade=\"\"/>"]
            replace_paginate = "</div><div class=\"pagination__item\">"

            for break_page in break_page_list:
                document = document.replace(break_page,replace_paginate)

        return document
    
    data = paginate_document(data,children_count)
    return render_template('info_extraction.html',report=report, original_file=original_file,data=data,type='info_extraction')

@app.route("/confirm_info_extraction",methods=['POST'])
def confirm_info_extraction():
    if request.method == 'POST':
        data = eval(request.form["data"])
        # create json file
        original_file = data["original_file"]
        report_id = data["report_id"]
        category = data["category"]
        type = data["type"]
        folder_dir = original_file.split(".")[0]
        file_directory = folder_dir+"_"+type+".json"
        json_object = json.dumps(data,indent=4)
        with open(file_directory,"w") as outfile:
            outfile.write(json_object)
        # store the file directory to database
        json_file_num = JSON_file.query.filter_by(original_fileID=report_id,category=category).count()
        if json_file_num == 0:
            json_file = JSON_file(original_fileID=report_id,file_directory=file_directory,category=category)
            db.session.add(json_file)
        else:
            json_file = JSON_file.query.filter_by(original_fileID=report_id,category=category).first_or_404()
            json_file.file_directory = file_directory
        db.session.commit()
    return jsonify({"status": True, "data":data })

@app.route("/get_latest_info_extraction",methods=["POST"])
def get_latest_info_extraction():
    if request.method == 'POST':
        data = eval(request.form['data'])
        report_id = data['report_id']
        json_file_num = JSON_file.query.filter_by(original_fileID=report_id,category=4).count()
        if json_file_num != 0:
            json_file = JSON_file.query.filter_by(original_fileID=report_id,category=4).first_or_404()
            file_directory = json_file.file_directory
            f = open(file_directory)
            data = json.load(f)
            return jsonify({"status": True, "data":data })
    return jsonify({"status": False })

@app.route("/get_original_info_extraction",methods=["POST"])
def get_original_info_extraction():

    # create random color
    def getRandomColor(): 
        N = 10
        HSV_tuples = [(x * 1.0 / N, 0.5, 0.8) for x in range(N)]
        hex_out = []
        for rgb in HSV_tuples:
            rgb = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*rgb))
            hex_out.append('#%02x%02x%02x' % tuple(rgb))
        return hex_out

    if request.method == 'POST':
        
        data = eval(request.form['data'])
        file_dir = data["file_dir"]
        report_id = data['report_id']
        ori_info_extract_num = JSON_file.query.filter_by(original_fileID=report_id,category=3).count()
        if ori_info_extract_num != 0:
            json_file = JSON_file.query.filter_by(original_fileID=report_id,category=3).first_or_404()
            file_directory = json_file.file_directory
            f = open(file_directory)
            data = json.load(f)
            return jsonify({"status": True, "data":data })
        else:
            data,_ = model_info_extraction(file_dir)
            # create tag for each sentence
            text_label_JSON = {}
            text_label_JSON["res"]=[]

            data_keys = list(data.keys())
            tag_list =["Overview","Business Review","Performance","Prospect" ]
            color_list = getRandomColor()
            for i in range(len(tag_list)):
                currentTag = tag_list[i]
                currentColor = color_list[i]
                sentence_list = data[data_keys[i]]
                for sentence in sentence_list:
                    sentence =sentence.strip()
                    json_object ={}
                    json_object["content"] = sentence
                    json_object["tag"] = currentTag
                    json_object["color"]= currentColor
                    text_label_JSON["res"].append(json_object)
            # print(text_label_JSON)
            return jsonify({"status": False, "data":text_label_JSON })
     
    return jsonify({"status": False })  



