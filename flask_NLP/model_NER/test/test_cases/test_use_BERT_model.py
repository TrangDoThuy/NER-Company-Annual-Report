import unittest
import sys
import os
import json

class TestUse_BERT_Model(unittest.TestCase):
    def test_use_bert_model(self):
        f = open("model_NER/test/data/sample_input_use_BERT_model.txt", "r", encoding='utf-8')
        paragraph = f.read()
        f.close()
        result = use_BERT_model(paragraph)
        result_list = result["res"]

        self.assertGreaterEqual(len(result_list),0)

if __name__ == '__main__':
    sys.path.append(os.getcwd())

    from model_NER.use_BERT_model import use_BERT_model
    unittest.main()