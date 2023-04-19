# -*- coding: utf-8 -*-
import sys
from collections import OrderedDict

import torch
from transformers import AutoConfig, AutoTokenizer

from PraticeOfTransformers.CustomModelForNSPQABILSTM import CustomModelForNSPQABILSTM
from PraticeOfTransformers.CustomModelForNer import BertForNerAppendBiLstmAndCrf

model_name = 'bert-base-chinese'

tokenizer = AutoTokenizer.from_pretrained(model_name)

path = "./model_path/qa_path/ultimate_dict_nsp_qa_lstm_epoch_1000"

'''
问答部分
'''

if path != "":

    config = AutoConfig.from_pretrained(pretrained_model_name_or_path=model_name, num_labels=2)
    model = CustomModelForNSPQABILSTM(config)
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
    model = CustomModelForNSPQABILSTM.from_pretrained(
        pretrained_model_name_or_path=model_name)  # num_labels 测试用一下，看看参数是否传递

# 看是否用cpu或者gpu训练
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model.to(device)
def get_qa_result(question_passage_list):
        with torch.no_grad():
            encoded_dict = tokenizer.batch_encode_plus(
                batch_text_or_text_pairs=list(
                    zip(["春秋版画博物馆是坐落于北京的一所主要藏品为版画的博物馆。"], ["春秋版画博物馆在哪里？"])),
                # 输入文本对 # 输入文本,采用list[tuple(text,question)]的方式进行输入
                add_special_tokens=True,  # 添加 '[CLS]' 和 '[SEP]'
                max_length=512,  # 填充 & 截断长度
                truncation=True,
                padding='longest',
                return_attention_mask=True,  # 返回 attn. masks.
            )
            model_output = model(input_ids=torch.tensor(encoded_dict['input_ids']).to(device),
                                 attention_mask=torch.tensor(encoded_dict['attention_mask']).to(device),
                                 token_type_ids=torch.tensor(encoded_dict['token_type_ids']).to(device))
            qa_start_logits = model_output.qa_start_logits.to("cpu")
            qa_end_logits = model_output.qa_end_logits.to("cpu")



