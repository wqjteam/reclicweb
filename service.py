from datetime import datetime
import json

import torch

import mysqldao
import ner_model_inference
import pojo
import qa_model_inference
nsp_id_label = {1: True, 0: False}

nsp_label_id = {True: 1, False: 0}

def search_data(data: pojo.SearchHistoryPojo):
    mysqldao.insert_history(data)
    ner_result=ner_model_inference.get_ner_result(data.search_data)

    passage_list=['春秋版画博物馆是坐落于北京的一所主要藏品为版画的博物馆。',
     '上海市立博物馆原址在江湾乡，为仿欧美新型综合性博物馆，民国26年1月10日正式开放。1951年11月，并入上海博物馆筹备处，迁址河南南路16号。',
     '国家民权博物馆位于美国中南部孟菲斯市是美国著名的民权运动城市，美国民权领袖马丁·路德·金1968年在位于该市的一家汽车旅馆遇刺身亡，该旅馆随后被改建为美国国家民权博物馆。',
     '三国青瓷虎头三足洗此展品为三国·吴时期文物。盥洗或盛食容器。宽唇上翘，敛口，鼓腹，平底内凹，有支钉痕，底置虎头形三足。现收藏绍兴博物馆。',
     '中号线装本剪纸毛泽东这套仿古线装本剪纸以毛泽东各个时期的照片为模本，剪刻而成，形象逼真，十分珍贵。现收藏于广灵剪纸艺术博物馆。',
     '唐鸾凤绶带纹葵形铜镜此展品为唐朝文物，葵形，圆钮，花瓣形钮座。左右饰对称鸾凤衔绶纹，上下饰对称神兽纹。素缘。现收藏于九江市博物馆。']

    ner_pass_pair_list=[(passage,data.search_data) for passage in passage_list]


    model_out=qa_model_inference.get_qa_result(ner_pass_pair_list)
    relation_score_argmax=torch.argmax(model_out[0],dim=1)
    relation_score_argmax
    relation_score_softmax=torch.softmax(model_out[0],dim=1).tolist()

    start_position=torch.argmax(model_out[1],dim=1).tolist()
    end_position=torch.argmax(model_out[2],dim=1).tolist()
    return "zhegshi fanhuishuju"


def get_front_hinstory_data(data: pojo.SearchHistoryPojo):
    returndata= mysqldao.get_history_front_data(data)
    returnjosnstr=json.dumps(returndata, cls=DateEncoder,ensure_ascii=False)
    return returnjosnstr


def get_backward_hinstory_data(mac_address, index, rows):
    mysqldao.get_history_backward_data(mac_address, index, rows)
    return "zhegshi fanhuishuju"


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)