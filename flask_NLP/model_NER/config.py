import transformers 

MAX_LEN = 128
BASE_MODEL_PATH = "model_NER/input/bert_base_uncased"
TOKENIZER = transformers.BertTokenizer.from_pretrained(
        BASE_MODEL_PATH,
        do_lower_case=True
    )