# -*- coding: utf-8 -*-
from collections import OrderedDict

import torch
from transformers import AutoConfig, AutoTokenizer

from PraticeOfTransformers.CustomModelForNer import BertForNerAppendBiLstmAndCrf

model_name = 'bert-base-chinese'

tokenizer = AutoTokenizer.from_pretrained(model_name)


'''
实体识别部分
'''
ner_id_label = {0: '[CLS]', 1: '[SEP]', 2: 'O', 3: 'B-ORG', 4: 'B-PER', 5: 'B-LOC', 6: 'B-TIME', 7: 'B-BOOK',
                8: 'I-ORG', 9: 'I-PER', 10: 'I-LOC', 11: 'I-TIME', 12: 'I-BOOK'}
ner_label_id = {}
for key in ner_id_label:
    ner_label_id[ner_id_label[key]] = key

config = AutoConfig.from_pretrained(pretrained_model_name_or_path=model_name, num_labels=len(ner_label_id))
model = BertForNerAppendBiLstmAndCrf(config)
# 因为后面的参数没有初始化，所以采用非强制性约束
state_dict =torch.load("")

new_state_dict = OrderedDict()
for k, v in state_dict.items():  # k为module.xxx.weight, v为权重
    if k.startswith('module.'):
        name = k[7:]  # 截取`module.`后面的xxx.weight
        new_state_dict[name] = v
    else:
        new_state_dict[k] = v

# 因为后面的参数没有初始化，所以采用非强制性约束,多GPu的加载到单GPU上需要, map_location='cuda:0'
model.load_state_dict(new_state_dict, strict=True)


model()
