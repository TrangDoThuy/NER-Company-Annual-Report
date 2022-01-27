import unittest
import sys
import os
import json

class TestExtractListTables(unittest.TestCase):
    def test_remove_unnecessary_letter(self):
        input_string = " Item&nbsp;1<"
        expected_output = "Item 1<"
        result = remove_unnecessary_letter(input_string)
        self.assertEqual(expected_output, result)

    def test_extract_item_1_business(self):
        f = open("test/data/sample_raw_item1.txt", "r")
        data = f.read()
        file_path = "test/data/annual_report_2008-12-19_a2189713z10-k.htm"
        output = extract_item_1_business(file_path)
        self.assertEqual(output,data)
        f.close()

    def test_extract_item_7(self):
        f = open("test/data/sample_raw_item7.txt", "r", encoding='utf-8')
        data_7 = f.read()
        file_path = "test/data/annual_report_2008-12-19_a2189713z10-k.htm"
        output_7 = extract_item_7_financial_analyse(file_path)
        self.assertEqual(output_7,data_7)
        f.close()

    def test_generate_header_content_1(self):
        f = open("test/data/sample_raw_item1.txt", "r")
        raw_text_item_1 = f.read()
        f.close()
        object_list_item_1 = generate_header_content(raw_text_item_1)

        file = open("test/data/sample_list_item_1.json")
        data = json.load(file)
        file.close()
        self.assertEqual(object_list_item_1,data)

    def test_generate_header_content_7(self):
        f = open("test/data/sample_raw_item7.txt", "r", encoding='utf-8')
        raw_text_item_7 = f.read()
        f.close()
        object_list_item_7 = generate_header_content(raw_text_item_7)

        file = open("test/data/sample_list_item_7.json", encoding='utf-8')
        data = json.load(file)
        file.close()
               
        self.assertEqual(object_list_item_7,data)

    def test_extract_overview_and_business_review(self):
        file = open("test/data/sample_list_item_1.json")
        object_list_item_1 = json.load(file)
        file.close()
        overview, business_review =  extract_overview_and_business_review(object_list_item_1)
        
        f = open("test/data/sample_overview.txt", "r")
        sample_overview = f.read()
        f.close()

        f = open("test/data/sample_business_review.txt", "r")
        sample_business_review = f.read()
        f.close()

        self.assertEqual(overview,sample_overview)
        self.assertEqual(business_review, sample_business_review)

    def test_performance_extraction(self):
        file = open("test/data/sample_list_item_7.json")
        object_list_item_7 = json.load(file)
        file.close()
        performance = performance_extraction(object_list_item_7)
        
        f = open("test/data/sample_performance.txt", "r")
        sample_performance = f.read()
        f.close()

        self.assertEqual(performance,sample_performance)

    def test_prospects_extraction(self):
        file = open("test/data/sample_list_item_7.json")
        object_list_item_7 = json.load(file)
        file.close()

        prospect_paragraph = ""
        for item in prospects_extraction(object_list_item_7):
            prospect_paragraph = prospect_paragraph + item + "  "

        f = open("test/data/sample_prospect.txt", "r")
        sample_prospect = f.read()
        f.close()
        self.assertEqual(prospect_paragraph, sample_prospect)

    def test_model_info_extraction(self):
        file_path = "test/data/annual_report_2008-12-19_a2189713z10-k.htm"
        result,_ = model_info_extraction(file_path)

        file = open("test/data/sample_result_info_extract.json")
        sample_result = json.load(file)
        file.close()

        self.assertEqual(result,sample_result)       

if __name__ == "__main__":
    sys.path.append(os.getcwd())

    from info_extraction import remove_unnecessary_letter, extract_item_1_business, extract_item_7_financial_analyse, generate_header_content, extract_overview_and_business_review, performance_extraction, prospects_extraction, model_info_extraction 
    unittest.main()