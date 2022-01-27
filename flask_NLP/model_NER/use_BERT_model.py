import json

import joblib
import torch

import model_NER.dataset as dataset
from model_NER.model import EntityModel

def use_BERT_model(paragraph):

    # paragraph = "Emma is from Vietnam. Nice to live in Hong Kong."
    paragraph =  paragraph.replace("U.S.","US").replace(". ","\n").replace("US","U.S.")
    sents = paragraph.split("\n")


    meta_data = joblib.load("model_NER/input/meta.bin")
    enc_tag = meta_data["enc_tag"]
    num_tag = len(list(enc_tag.classes_))

    texts_test_dataset = []
    tags_test_dataset = []
    for sent in sents:
        if(len(sent)<5):
            continue
        sent = sent.split(" ")
        texts_test_dataset.append(sent) 
        tags = [1]*len(sent) 
        tags_test_dataset.append(tags)    
    
    test_dataset = dataset.EntityDataset(
        texts = texts_test_dataset,
        tags = tags_test_dataset
        )

    device = torch.device("cuda")
    model = EntityModel( num_tag = num_tag)
    model.load_state_dict(torch.load("model_NER/input/model.bin"))
    
    model.to(device)

    text_label_raw = {}
    text_label_raw["res"] = []

    with torch.no_grad():
        for sent_idx, data in enumerate(test_dataset):
            for k,v in data.items():
                data[k] = v.to(device).unsqueeze(0)
            tags,_,_ = model(**data)
            tag_list =  enc_tag.inverse_transform(
                    tags.argmax(2).cpu().numpy().reshape(-1)
                    )[1:]
            for word_idx, tag in enumerate(tag_list):
                if tag != "0" and tag != "O" and word_idx < len(texts_test_dataset[sent_idx]):
                    obj = {}
                    obj["content"] = texts_test_dataset[sent_idx][word_idx]
                    if(obj["content"]=="us"):
                        continue
                    obj["tag"] = tag
                    obj["index"] = word_idx
                    text_label_raw["res"].append(obj)

    f = open('model_NER/input/tag2name_color.json')
    tag2name_color = json.load(f)
    f.close()


    text_label_JSON = {}
    text_label_JSON["res"]=[]

    prev_obj = {}
    prev_obj["content"] = ""
    prev_obj["tag"] = "_"
    prev_obj["index"] = -1

    for obj in text_label_raw["res"]:
        if obj["tag"][0] == 'B':
            if prev_obj["tag"][0] == 'B':
                prev_obj["tag"] = prev_obj["tag"][2:]
                text_label_JSON["res"].append(prev_obj)
            prev_obj = obj
        elif obj["tag"][0] == 'I' and prev_obj["tag"][0] == 'B' and obj["tag"][1:] == prev_obj["tag"][1:] and prev_obj["index"]+1 == obj["index"]: 
            prev_obj["content"] += (" "+obj["content"])
            prev_obj["index"] += 1
        elif prev_obj["tag"][0] == 'B':
            prev_obj["tag"] = prev_obj["tag"][2:]
            text_label_JSON["res"].append(prev_obj)
            prev_obj = obj
    if prev_obj["tag"][0] == 'B':
        prev_obj["tag"] = prev_obj["tag"][2:]
        text_label_JSON["res"].append(prev_obj)

    for obj in text_label_JSON["res"]:
        tag_obj = tag2name_color[obj["tag"]]
        obj["tag"] = tag_obj["name"]
        obj["color"] = tag_obj["color"]

    # print("======= text_label_JSON ===============")
    # print(text_label_JSON) 

    return text_label_JSON   

                

# use_BERT_model("hihih")