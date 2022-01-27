import model_NER.config as config
import model_NER.utils as utils 
import torch
import transformers
import torch.nn as nn


def loss_fn(output,target,mask, num_lables):
    lfn = nn.CrossEntropyLoss()
    active_loss = mask.view(-1) == 1
    active_logits = output.view(-1,num_lables)
    active_labels = torch.where(
        active_loss,
        target.view(-1),
        torch.tensor(lfn.ignore_index).type_as(target)
    )

    loss = lfn(active_logits,active_labels)
    return loss

def accuracy_fn(output,target,mask):
    output = output.argmax(2)
    real_output = torch.flatten(mask*output)
    real_target = torch.flatten(mask*target)
    score = 0.0
    total = 1
    for i in range(len(real_target)):
        if real_target[i] !=0:
            total += 1
            if real_target[i] == real_output[i]:
                score +=1
    return score/total


class EntityModel(nn.Module):
    def __init__(self, num_tag):
        super(EntityModel, self).__init__()
        self.num_tag = num_tag
        self.bert = transformers.BertModel.from_pretrained(config.BASE_MODEL_PATH,return_dict=False)
        self.bert_drop_1 = nn.Dropout(0.3)
        self.out_tag = nn.Linear(768,self.num_tag)
        

    def forward(self,ids,mask,token_type_ids,target_tag,valid_mask):

        o1, _ = self.bert(ids,attention_mask=mask,token_type_ids=token_type_ids)
        bo_tag = self.bert_drop_1(o1)
        tag = self.out_tag(bo_tag)
        tag, mask = utils.valid_sequence_output(tag,valid_mask,mask)
        loss = loss_fn(tag,target_tag,mask,self.num_tag)
        accuracy_score = accuracy_fn(tag,target_tag,mask)

        return tag,loss,accuracy_score

