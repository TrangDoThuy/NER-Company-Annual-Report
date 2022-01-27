import unittest
import sys
import os
import json
from bs4 import BeautifulSoup

class TestExtractListTables(unittest.TestCase):
    def test_extract_list_tables_0(self):
        file_path = "hihi"
        result = extract_list_tables(file_path)
        self.assertIsNone(result)
    
    def test_extract_list_tables_1(self):
        file_path = "test/data/annual_report_2008-12-19_a2189713z10-k.htm"
        result_table_json = extract_list_tables(file_path)

        f = open('test/data/sample_tables_json.json')
        data = json.load(f)
        f.close()
        self.assertEqual(result_table_json,data)
        

    def test_check_quantitative_table(self):
        file_path = "test/data/annual_report_2008-12-19_a2189713z10-k.htm"
        
        with open(file_path, 'r', errors='backslashreplace') as file:
            content = file.read()
    

        soup = BeautifulSoup(content,"lxml")

        tables = soup.findAll("table")
        quant = check_quantitative_table(tables[0])

        self.assertEqual(quant,True)
    
    def test_extract_table(self):
        file_path = "test/data/annual_report_2008-12-19_a2189713z10-k.htm"
        list_file_path = extract_table(file_path)

        f = open('test/data/sample_list_file_path.json')
        data = json.load(f)
        f.close()
        self.assertEqual(list_file_path,data)

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    from extract_list_tables import check_quantitative_table, extract_list_tables, extract_table
    unittest.main()