import math
from datetime import datetime
import json

import torch

import mysqldao
import elasticsearchdao
import ner_model_inference
import pojo
import qa_model_inference

nsp_id_label = {1: True, 0: False}

nsp_label_id = {True: 1, False: 0}
threshold = 0.01

"""

历史记录相关
"""


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
    relation_score_max_index = torch.argmax(torch.softmax(model_out[0], dim=1)[:, 1], dim=0)  # 获取在true位置最大得passage
    relation_score_softmax = torch.argmax(torch.softmax(model_out[0], dim=1), dim=0)  # 获取所有位置最大得

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


def update_history_data(id, update_time, aduit):
    returndata = mysqldao.update_history(id, update_time, aduit)
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


"""
admin 相关
"""


def create_admin(username, password, work_no):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    admin = pojo.AdminPojo(username=username, password=password, work_no=work_no, status=-1, create_time=now,
                           update_time=now)
    prejudge = mysqldao.create_admin_pre(admin)
    if (prejudge > 0):
        returndict = {"data": {}, 'status': -1}
    else:

        mysqldao.create_admin(admin)
        returndict = {"data": {}, 'status': 0}

    returnjosnstr = json.dumps(returndict, cls=DateEncoder, ensure_ascii=False)
    return returnjosnstr


def get_backward_login(data: pojo.AdminPojo):
    result = mysqldao.login_backward(data)
    if len(result) == 0:
        return -1
    else:
        return result[0][0]


def get_admin_page(work_no: str, pageindex: int = 1, pagerows: int = 10):
    amount = mysqldao.get_admin_data_segment_amount(work_no)
    adminlist = mysqldao.get_admin_data_segment_page(work_no, pageindex=pageindex, pagerows=pagerows)

    returndict = {"data": {
        "pages": math.ceil(amount / pagerows),
        "records": adminlist
    }, 'status': 0
    }

    returnjosnstr = json.dumps(returndict, cls=DateEncoder, ensure_ascii=False)
    return returnjosnstr


def update_admin_password(id: int = 0, password=None):
    admin = pojo.AdminPojo(id=id, password=password)
    result = mysqldao.update_admin_password(admin)
    return result


def update_admin_self(id: int = 0, username=None, password=None, work_no=None):
    admin = pojo.AdminPojo(id=id, username=username, password=password, work_no=work_no)
    preresult = mysqldao.judge_admin_update_pre(admin)
    if len(preresult) > 0:
        returndict = {"data": {}, 'status': -1}
    else:

        mysqldao.update_admin(admin)
        returndict = {"data": {}, 'status': 0}
    returnjosnstr = json.dumps(returndict, cls=DateEncoder, ensure_ascii=False)
    return returnjosnstr


def admin_audit(id, audit):
    admin = pojo.AdminPojo(id=id, status=audit)
    preresult = mysqldao.update_admin_audit(admin)
    return preresult


"""
审核文章相关
"""


def get_passage_audit_page(blurcontent: str, pageindex: int = 1, pagerows: int = 10):
    passage_page = elasticsearchdao.get_search_result_page(blurcontent=blurcontent, pageindex=pageindex,
                                                           pagerows=pagerows)
    passage_page_amount = elasticsearchdao.get_search_result_amount(blurcontent=blurcontent)
    es_data = passage_page['hits']['hits']
    es_ids = [a['_id'] for a in es_data]
    data_dict = mysqldao.get_passage_audit_all_data_byesids(es_ids)
    pads = [pojo.PassageAuditDto(es_id=a['_id'], es_data=a['_source']['info']) for a in es_data]
    for pad in pads:
        passageaudit = data_dict.get(pad.es_id, None)
        if passageaudit is not None:
            pad.id = passageaudit.id
            pad.audit = passageaudit.audit
            pad.create_time = passageaudit.create_time
            pad.update_time = passageaudit.update_time
        else:
            pad.create_time = datetime.now()
            pad.update_time = datetime.now()

    returndict = {"data": {
        "pages": math.ceil(passage_page_amount['count'] / pagerows),
        "records": pads
    }, 'status': 0
    }

    returnjosnstr = json.dumps(returndict, cls=DateEncoder, ensure_ascii=False)
    return returnjosnstr


def insert_update_audit_passage(dto: pojo.PassageAudit):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if dto.id == 0 or dto.id == '0':
        # 则是插入
        pa = pojo.PassageAudit(es_id=dto.es_id, audit=dto.audit, create_time=now, update_time=now)
        result = mysqldao.insert_passage(pa)
    else:
        # 则是修改
        result = mysqldao.passage_update_audit(id=dto.id, audit=dto.audit)
    return result


"""
json解析器
"""


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
        elif isinstance(obj, pojo.PassageAuditDto):
            return {'id': obj.id, 'es_id': obj.es_id, 'es_data': obj.es_data, 'audit': obj.audit,
                    'create_time': obj.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'update_time': obj.update_time.strftime("%Y-%m-%d %H:%M:%S")}
        elif isinstance(obj, pojo.AdminPojo):
            return {'id': obj.id, 'username': obj.username, 'password': obj.password, 'work_no': obj.work_no,'status': obj.status,
                    'create_time': obj.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'update_time': obj.update_time.strftime("%Y-%m-%d %H:%M:%S")}
        else:
            return json.JSONEncoder.default(self, obj)
