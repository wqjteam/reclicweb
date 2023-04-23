import json

import pymysql
from sqlalchemy import create_engine
# from sqlalchemy.dialects.mysql import pymysql

import pojo
import service

conn = pymysql.Connect(
    host='47.120.39.188',
    port=3306,
    user='root',
    passwd='qwertyuiop123456',
    db='relic_data',
    charset='utf8'
)

engine = create_engine("mysql+pymysql://root:123456@192.168.4.110:3306/relic_data?charset=utf8")


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
