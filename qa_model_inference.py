# -*- coding: utf-8 -*-
import sys
from collections import OrderedDict

import torch
from transformers import AutoConfig, AutoTokenizer

from PraticeOfTransformers.CustomModelForNSPQABILSTM import CustomModelForNSPQABILSTM
from PraticeOfTransformers.CustomModelForNer import BertForNerAppendBiLstmAndCrf

model_name = 'bert-base-chinese'

tokenizer = AutoTokenizer.from_pretrained(model_name)


'''
问答部分
'''


if len(sys.argv) >= 1:

    config = AutoConfig.from_pretrained(pretrained_model_name_or_path=model_name, num_labels=len(ner_label_id))
    model = CustomModelForNSPQABILSTM(config)
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
else:
    model = CustomModelForNSPQABILSTM.from_pretrained(pretrained_model_name_or_path=model_name)  # num_labels 测试用一下，看看参数是否传递
with torch.no_grad():
    model