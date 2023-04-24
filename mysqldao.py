import json


import pymysql
from sqlalchemy import create_engine


import pojo

conn = pymysql.Connect(
    host='47.120.39.188',
    port=3306,
    user='root',
    passwd='qwertyuiop123456',
    db='relic_data',
    charset='utf8'
)

engine = create_engine("mysql+pymysql://root:123456@192.168.4.110:3306/relic_data?charset=utf8")

"""
history表
"""


def insert_history(search_data: pojo.SearchHistoryPojo):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    sql_insert = search_data.get_insert_sql()
    cursor.execute(sql_insert)
    cursor.close()
    conn.commit()
    conn.close()


def get_history_front_data(search_data: pojo.SearchHistoryPojo):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    sql_fetchall = search_data.get_front_history_sql()
    cursor.execute(sql_fetchall)
    result = cursor.fetchall()
    return_data = [list(a) for a in result]
    cursor.close()
    conn.close()
    return return_data


def get_history_backward_data(mac_address, search_data, index, rows):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    search_data_pojo = pojo.SearchHistoryPojo()
    sql_fetchall = search_data_pojo.get_backword_history_sql_page(mac_address, search_data, index, rows)
    cursor.execute(sql_fetchall)
    result_fecthall = cursor.fetchall()
    result = [pojo.SearchHistoryPojo(r[0], r[1], r[2], r[3], r[4], r[5]) for r in result_fecthall]

    cursor.close()
    conn.close()
    return result


def get_history_backward_amount(mac_address, search_data_str):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    search_data = pojo.SearchHistoryPojo()
    sql_fetchall = search_data.get_backword_history_amount(mac_address=mac_address, search_data=search_data_str)
    cursor.execute(sql_fetchall)
    result = cursor.fetchall()
    return result[0][0]


def update_history(id, update_time, audit):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    search_data = pojo.SearchHistoryPojo()
    sql = search_data.get_audit_history_sql(history_id=id, update_time=update_time, audit_status=audit)
    result = cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()
    return result


"""
admin表
"""

def create_admin_pre(admin:pojo.AdminPojo):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    sql=admin.get_register_pre_sql()
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data = [a for a in result]
    cursor.close()
    conn.close()
    return return_data



def create_admin(admin:pojo.AdminPojo):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    sql=admin.get_register_sql()
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data = [a for a in result]
    cursor.close()
    conn.close()
    return return_data


def login_backward(admin: pojo.AdminPojo):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    sql_login = admin.get_login_sql()
    cursor.execute(sql_login)
    result = cursor.fetchall()
    return_data = [list(a) for a in result]
    cursor.close()
    conn.close()
    return return_data


def judge_admin_update_pre(admin: pojo.AdminPojo):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    sql = admin.get_update_username_pre_sql()
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data = [list(a) for a in result]
    cursor.close()
    conn.close()
    return return_data



def update_admin(admin: pojo.AdminPojo):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    sql = admin.get_update_admin_sql()
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data = [list(a) for a in result]
    cursor.close()
    conn.close()
    return return_data

def update_admin_audit(admin: pojo.AdminPojo):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    sql = admin.get_update_audit_sql()
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data = [list(a) for a in result]
    cursor.close()
    conn.close()
    return return_data


def update_admin_password(admin: pojo.AdminPojo):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    sql = admin.get_update_password_sql()
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data = [list(a) for a in result]
    cursor.close()
    conn.close()
    return return_data

def get_admin_data_segment_page(work_no=None, pageindex: int = 1, pagerows: int = 10):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    admin = pojo.AdminPojo
    sql = admin.get_data_segment_page(work_no=work_no, pageindex=pageindex, pagerows=pagerows)
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data = [pojo.AdminPojo(a[0], a[1], a[2], a[3], a[4], a[5], a[6]) for a in result]
    cursor.close()
    conn.close()
    return return_data


def get_admin_data_segment_amount(work_no=None):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    admin = pojo.AdminPojo
    sql = admin.get_admin_data_amount(work_no=work_no)
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data = [a for a in result]
    cursor.close()
    conn.close()
    return return_data[0][0]


"""
文本表
"""


def insert_passage(passage: pojo.PassageAudit):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    sql = passage.get_alldata_sql()
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data = [a for a in result]
    return return_data


def get_passage_audit_all_data():
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    passage = pojo.PassageAudit()
    sql = passage.get_alldata_sql()
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data = [pojo.PassageAudit(a[0], a[1], a[2], a[3], a[4]) for a in result]
    cursor.close()
    conn.close()
    return return_data


def get_passage_audit_all_data_byesids(esids):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    passage = pojo.PassageAudit()
    sql = passage.get_alldata_sql_byids(esids)
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data_dict = {a[1]: pojo.PassageAudit(a[0], a[1], a[2], a[3], a[4]) for a in result}
    cursor.close()
    conn.close()
    return return_data_dict


def passage_update_audit(id, audit):
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    passage = pojo.PassageAudit()
    sql = passage.get_passage_update_audit_sql(id=id, audit=audit)
    cursor.execute(sql)
    result = cursor.fetchall()
    return_data = [a for a in result]
    cursor.close()
    conn.close()
    return return_data
