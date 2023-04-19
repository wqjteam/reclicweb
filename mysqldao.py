import pymysql
from sqlalchemy import create_engine
# from sqlalchemy.dialects.mysql import pymysql

import pojo

conn = pymysql.Connect(
    host='2234p94b30.imdo.co',
    port=54833,
    user='root',
    passwd='123456',
    db='relic_data',
    charset='utf8'
)
cursor = conn.cursor()
engine = create_engine("mysql+pymysql://root:123456@192.168.4.110:3306/relic_data?charset=utf8")


def insert_history(search_data: pojo.SearchHistoryPojo):

    sql_insert = search_data.get_insert_sql()
    cursor.execute(sql_insert)
    conn.commit()
    # conn.close()
    # cursor.close()


def get_history_front_data(search_data: pojo.SearchHistoryPojo):

    sql_fetchall = search_data.get_front_history_sql()
    cursor.execute(sql_fetchall)
    result = cursor.fetchall()
    return_data = [list(a) for a in result]
    # cursor.close()
    return return_data


def get_history_backward_data(search_data: pojo.SearchHistoryPojo):

    sql_fetchall = search_data.get_front_history_sql()
    cursor.execute(sql_fetchall)
    result = cursor.fetchall()
    for a in result:
        print(a)
    # cursor.close()
