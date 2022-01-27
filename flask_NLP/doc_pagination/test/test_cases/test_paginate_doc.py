import unittest
import sys
import os
import json

class TestDocPagination(unittest.TestCase):
    def test_paginate_doc(self):
        f = open("model_NER/test/data/sample_input_use_BERT_model.txt", "r", encoding='utf-8')
        paragraph = f.read()
        f.close()
        result = use_BERT_model(paragraph)
        result_list = result["res"]

        self.assertGreaterEqual(len(result_list),0)

if __name__ == '__main__':
    sys.path.append(os.getcwd())

    from paginate_doc import paginate_doc
    unittest.main()