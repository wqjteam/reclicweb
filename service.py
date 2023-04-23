import math
from datetime import datetime
import json

import torch

import elasticsearchdao
import mysqldao
import ner_model_inference
import pojo
import qa_model_inference

nsp_id_label = {1: True, 0: False}

nsp_label_id = {True: 1, False: 0}
threshold = 0.01


def search_data(data: pojo.SearchHistoryPojo):
    mysqldao.insert_history(data)
    ner_result = ner_model_inference.get_ner_result(data.search_data)
    passage_list = []
    es_search_result = elasticsearchdao.get_search_result(ner_result)

    if es_search_result['hits']['max_score'] is None or es_search_result['hits']['max_score'] <= threshold:
        return "无答案"
    else:
        es_search_result['hits']['hits'].sort(key=lambda x: x['_score'], reverse=True)
        for index, doc in enumerate(es_search_result['hits']['hits']):
            if index < 5 and doc['_score'] > threshold:
                passage_list.append(doc['_source']['info'])
            else:
                break

    ner_pass_pair_list = [(passage, data.search_data) for passage in passage_list]

    model_out = qa_model_inference.get_qa_result(ner_pass_pair_list)
    relation_score_argmax: torch.tensor = torch.argmax(model_out[0], dim=1)
    if torch.sum(relation_score_argmax) == 0:
        return "无答案"
    relation_score_max_index = torch.argmax(torch.softmax(model_out[0], dim=1)[:, 1], dim=0)
    relation_score_softmax = torch.argmax(torch.softmax(model_out[0], dim=1), dim=0)

    start_position = torch.argmax(model_out[1], dim=1).tolist()[relation_score_max_index]
    end_position = torch.argmax(model_out[2], dim=1).tolist()[relation_score_max_index]
    if start_position == end_position:
        return "无答案"
    hit_result = model_out[3][relation_score_max_index]
    result = hit_result[start_position:end_position]
    return ''.join(result)


def get_front_history_data(data: pojo.SearchHistoryPojo):
    returndata = mysqldao.get_history_front_data(data)
    returnjosnstr = json.dumps(returndata, cls=DateEncoder, ensure_ascii=False)
    return returnjosnstr


def update_history_data(id,update_time, aduit):
    returndata = mysqldao.update_history(id,update_time, aduit)
    returndatastr = {
        'status': 0,
        "data": {}
    }
    if returndata <= 0:
        returndatastr['status'] = -1

    return json.dumps(returndatastr)


def get_backward_history_data(mac_address, search_data, index, rows=10):
    amount = mysqldao.get_history_backward_amount(mac_address, search_data)
    data = mysqldao.get_history_backward_data(mac_address=mac_address, search_data=search_data, index=index, rows=rows)
    print(data)
    returndict = {"data": {
        "pages": math.ceil(amount / rows),
        "records": data
    }, 'status': 0
    }
    returnjosnstr = json.dumps(returndict, cls=DateEncoder, ensure_ascii=False)
    return returnjosnstr


def get_backward_login(data: pojo.AdminPojo):
    result = mysqldao.login_backward(data)
    if len(result) == 0:
        return -1
    else:
        return result[0][0]


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, pojo.SearchHistoryPojo):
            return {'id': obj.id, 'mac_address': obj.mac_address, 'search_data': obj.search_data,
                    'audit': obj.audit, 'insert_time': obj.insert_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'update_time': obj.update_time.strftime("%Y-%m-%d %H:%M:%S")}
        elif isinstance(obj, pojo.PassageAudit):
            return {'id': obj.id, 'es_id': obj.es_id, 'audit': obj.audit,
                    'create_time': obj.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'update_time': obj.update_time.strftime("%Y-%m-%d %H:%M:%S")}
        else:
            return json.JSONEncoder.default(self, obj)
