# -*- coding: utf-8 -*-
import sys
from collections import OrderedDict

import torch
from tokenizers import Tokenizer
from transformers import AutoConfig, AutoTokenizer, BertTokenizer

from PraticeOfTransformers.CustomModelForNer import BertForNerAppendBiLstmAndCrf

model_name = 'bert-base-chinese'

tokenizer = BertTokenizer.from_pretrained(model_name)

path = "./model_path/ner_path/ultimate_dict_ner_epoch_1000"

'''
实体识别部分
'''
ner_id_label = {0: '[CLS]', 1: '[SEP]', 2: 'O', 3: 'B-ORG', 4: 'B-PER', 5: 'B-LOC', 6: 'B-TIME', 7: 'B-BOOK',
                8: 'I-ORG', 9: 'I-PER', 10: 'I-LOC', 11: 'I-TIME', 12: 'I-BOOK'}
ner_label_id = {}
for key in ner_id_label:
    ner_label_id[ner_id_label[key]] = key

if path != "":

    config = AutoConfig.from_pretrained(pretrained_model_name_or_path=model_name, num_labels=len(ner_label_id))
    model = BertForNerAppendBiLstmAndCrf(config)
    # 因为后面的参数没有初始化，所以采用非强制性约束
    state_dict = torch.load(path)

    new_state_dict = OrderedDict()
    for k, v in state_dict.items():  # k为module.xxx.weight, v为权重
        if k.startswith('module.'):
            name = k[7:]  # 截取`module.`后面的xxx.weight
            new_state_dict[name] = v
        else:
            new_state_dict[k] = v

    # 因为后面的参数没有初始化，所以采用非强制性约束,多GPu的加载到单GPU上需要, map_location='cuda:0'
    model.load_state_dict(new_state_dict, strict=True)

else:
    model = BertForNerAppendBiLstmAndCrf.from_pretrained(
        pretrained_model_name_or_path=model_name)  # num_labels 测试用一下，看看

# 看是否用cpu或者gpu训练
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model.to(device)
def get_ner_result(input_question):
    with torch.no_grad():
        encode_dict = tokenizer.encode_plus(text=input_question,
                                             add_special_tokens=True,
                                             truncation=True)
        input_ids = encode_dict['input_ids']
        token_type_ids = encode_dict['token_type_ids']
        # labels = encode_dict['labels']
        _, logits = model(torch.tensor([input_ids]).to(device), token_type_ids=torch.tensor([token_type_ids]).to(device),
                          is_test=True,
                          labels=torch.ones_like(torch.tensor([input_ids])).to(device))
        predict = logits.view(-1, logits.shape[2])[0].cpu().tolist()
        print("结果输出")
        returnlist=[]
        returnindex=-1
        for index,tp in enumerate(zip(tokenizer.convert_ids_to_tokens(encode_dict['input_ids']), predict)):
            print(tp[0] + '\001' + ner_id_label[tp[1]])
            if ner_id_label[tp[1]].startswith('B'):
                returnindex=returnindex+1
                returnlist.append(tp[0])
            elif ner_id_label[tp[1]].startswith('I'):

                returnlist[returnindex]=returnlist[returnindex]+tp[0]
            else:
                pass
        return returnlist

get_ner_result("春秋版画博物馆在哪里？")