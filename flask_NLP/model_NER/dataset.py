import model_NER.config as config
import torch

class EntityDataset:
    def __init__(self,texts,tags):
        # texts: [["hi",",","I","am","learning"],["hello"," ","nice","to","meet","you"]]
        # pos/tags: [[1 2 3 4 5],[2 3 4 5 6]]
        self.texts = texts
        self.tags = tags

    def __len__(self):
        return len(self.texts)
    def __getitem__(self,item):
        text = self.texts[item]
        tags = self.tags[item]


        ids = []
        target_tag = tags
        valid_mask = []

        for i,s in enumerate(text):
            inputs = config.TOKENIZER.tokenize(s)
            for j,token in enumerate(inputs):
                if j == 0:
                    valid_mask.append(1)
                else:
                    valid_mask.append(0)
            # hello: he ##llo
            ids.extend(inputs)
            
        ids = config.TOKENIZER.convert_tokens_to_ids(ids)
        ids = ids[:config.MAX_LEN -2]
        valid_mask = valid_mask[:config.MAX_LEN -2]
        target_tag = target_tag[:config.MAX_LEN -2]

        mask = [1]*len(ids)

        ids = [101] + ids + [102]
        target_tag = [0] + target_tag + [0]
        valid_mask = [1] + valid_mask + [1]
        mask = [0]+mask+[0]

        token_type_ids = [0]*config.MAX_LEN

        padding_len = config.MAX_LEN - len(ids)

        ids = ids + [0]*padding_len
        mask = mask + [0]*padding_len
        valid_mask = valid_mask + [0]*padding_len
        
        other_padding_len = config.MAX_LEN - len(target_tag)
        target_tag = target_tag + [0]*other_padding_len

        assert len(ids) == config.MAX_LEN 
        assert len(mask) == config.MAX_LEN 
        assert len(token_type_ids) == config.MAX_LEN 
        assert len(target_tag) == config.MAX_LEN 
        assert len(valid_mask) == config.MAX_LEN 

        return {
            "ids":torch.tensor(ids, dtype=torch.long),
            "mask":torch.tensor(mask, dtype=torch.long),
            "token_type_ids":torch.tensor(token_type_ids, dtype=torch.long),
            "target_tag":torch.tensor(target_tag, dtype=torch.long),
            "valid_mask":torch.tensor(valid_mask, dtype=torch.long)
        }