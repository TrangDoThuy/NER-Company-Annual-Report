# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 15:05:08 2021

@author: trang
"""

# Python program to read
# json file
 
 
import json
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn
def create_project(conn, report):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO reports(CIK,ticker,company_name,exchange,report_period,filing_date,source_url,file_directory)
              VALUES(?,?,?,?,?,?,?,?);  '''
    cur = conn.cursor()
    cur.execute(sql, report)
    conn.commit()
    return cur.lastrowid

def main():
 
    database = "annual_reports.db"
    # create a database connection
    conn = create_connection(database)
    
    # Opening JSON file
    f = open('meta_data.json')
     
    # returns JSON object as
    # a dictionary
    data = json.load(f)
     
    # Iterating through the json
    # list
    with conn:
        for company in data['companies']:
            reports = company["annual_reports"]
            for report in reports:
                report_object = {}
                report_object["CIK"] = company["CIK"]
                report_object["ticker"] = company["ticker"]
                report_object["conpany_name"] = company["name"]
                report_object["exchange"] = company["exchange"]
                report_object["report_period"] = report["report_period"]
                report_object["filing_date"] = report["filing_date"]
                report_object["source_url"] = report["source_url"]
                report_object["file_directory"] = report["file_directory"]
                report = (report_object["CIK"],report_object["ticker"],report_object["conpany_name"],report_object["exchange"],report_object["report_period"],report_object["filing_date"],report_object["source_url"],report_object["file_directory"])
                create_project(conn, report)
    # Closing file
    f.close()
    
if __name__ == '__main__':
    main()