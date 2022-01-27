import unittest
import sys
import os

class TestClassifyTable(unittest.TestCase):
    def test_table_classify_0(self):
        table_type, new_table_name, score = table_classify("hihi")
        self.assertEqual(table_type,-1)
        self.assertEqual(new_table_name,"others")
        self.assertEqual(score,0)

    def test_table_classify_1(self):
        f = open("test/data/content_table_0.txt", "r",encoding='utf-8')
        table_content = f.read()
        f.close()
        table_type, new_table_name, score = table_classify(table_content)
        self.assertEqual(table_type,1)
        self.assertEqual(new_table_name,"income_statement")
        self.assertEqual(score,0.03278688524590164)     

    def test_table_classify_2(self):
        f = open("test/data/sample_balance_sheet.txt", "r",encoding='utf-8')
        table_content = f.read()
        f.close()
        table_type, new_table_name, score = table_classify(table_content)
        self.assertEqual(table_type,2)
        self.assertEqual(new_table_name,"balance_sheet")
        self.assertEqual(score,0.42957746478873243)   

    def test_table_classify_3(self):
        f = open("test/data/sample_cash_flows.txt", "r",encoding='utf-8')
        table_content = f.read()
        f.close()
        table_type, new_table_name, score = table_classify(table_content)
        self.assertEqual(table_type,3)
        self.assertEqual(new_table_name,"cash_flows")
        self.assertEqual(score,0.3174061433447099)  

    def test_table_classify_4(self):
        f = open("test/data/sample_equity_statement.txt", "r",encoding='utf-8')
        table_content = f.read()
        f.close()
        table_type, new_table_name, score = table_classify(table_content)
        self.assertEqual(table_type,4)
        self.assertEqual(new_table_name,"equity_statement")
        self.assertEqual(score,0.17307692307692307)  

    def test_table_classify_5(self):
        f = open("test/data/sample_income_statement.txt", "r",encoding='utf-8')
        table_content = f.read()
        f.close()
        table_type, new_table_name, score = table_classify(table_content)
        self.assertEqual(table_type,1)
        self.assertEqual(new_table_name,"income_statement")
        self.assertEqual(score,0.19101123595505617) 


if __name__ == "__main__":
    sys.path.append(os.getcwd())
    from classify_table import table_classify
    unittest.main()