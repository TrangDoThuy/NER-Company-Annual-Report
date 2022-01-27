#%%
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import json
import os
#%%
df = pd.read_csv('cik_ticker.csv',sep="|")
#%%
f_json = open('meta_data.json')
json_object =json.load(f_json)
f_json.close()
endpoint = r"https://www.sec.gov/cgi-bin/browse-edgar"
#%%
print(df.loc[10399])
 
#%%
headers = { 'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" }
#json_object["companies"]=[]
exchange_list=[]
parent_dir = "Data/"
#%%
df_sub = df[10399:]
for index, row in df_sub.iterrows():
    print(index)
    if(index!=697):
        break

    company ={}
    company["CIK"] = row["CIK"]
    company["ticker"] = row["Ticker"]
    company["name"] = row["Name"]
    company["exchange"] = row["Exchange"]
    company["annual_reports"] = []
    
    exchange = company["exchange"]
    if(type(exchange)==float):
        exchange = "NaN"
    exchange_path = parent_dir+ exchange
    if not os.path.exists(exchange_path):
        os.makedirs(exchange_path)
        
    company_name = company["name"]
    company_cik = company["CIK"]
    company_path = exchange_path+"/"+ company_name
    if not os.path.exists(company_path):
        os.makedirs(company_path)
        
    param_dict_2 = {'action':'getcompany',
              'CIK':company_cik,
              'type':'10-k',
              'output':'atom'}
       
    response_10_K_list = requests.get(url = endpoint, params = param_dict_2,headers = headers)
    
    #time.sleep(0.1)
    soup_10_K_list = BeautifulSoup(response_10_K_list.content, ('html.parser'))
    print(soup_10_K_list)
    link_list = []
    
    
    for each_10_K in soup_10_K_list.find_all('entry'):
        link_10_K = each_10_K.find_all('link')[0]['href']
        link_list.append(link_10_K)

        response = requests.get(url = link_10_K,headers = headers)
        #time.sleep(0.1)
        soup = BeautifulSoup(response.content,('html.parser'))
        json_object_file ={}
        
        
        while(soup.find(text="Period of Report")==None):
            print("wait 10 mins")
            print(soup)
            time.sleep(600)
            response = requests.get(url = link_10_K,headers = headers)
            soup = BeautifulSoup(response.content,('html.parser'))
            
        report_period_title = soup.find(text="Period of Report")
        report_period = report_period_title.parent.findNext("div").text
        json_object_file["report_period"]=report_period
        filing_date_title = soup.find(text="Filing Date")
        filing_date = filing_date_title.parent.findNext("div").text
        json_object_file["filing_date"]=filing_date
        table = soup.find("table",{"summary":"Document Format Files"})
        row_10_K = table.find_all('tr')[1]
        cell_10_K_link = row_10_K.find_all('td')[2]
        
        link_10K = "https://www.sec.gov" +cell_10_K_link.find('a')['href']
        if(len(cell_10_K_link.find('a').text)==0):
            continue
        link_10K = link_10K.replace("/ix?doc=","")
        index_name = link_10K.rfind('/')
        name_file = link_10K[(index_name+1):]
        
        json_object_file["source_url"] = link_10K
        company["annual_reports"].append(json_object_file)
        
        # create 10-K file locally
        local_path = company_path+"/annual_report_"+filing_date+"_"+name_file

        r = requests.get(link_10K, stream=True, headers = headers)
        time.sleep(0.1)
        json_object_file["file_directory"] = local_path
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=10240):
                f.write(chunk)
        
    
    json_object["companies"].append(company)
    exchange_list.append(company["exchange"] )

#%%   

with open('meta_data.json', 'w', encoding='utf-8') as f:
    json.dump(json_object, f, ensure_ascii=False, indent=4)

#%%
print("hihi")
#%%
    
