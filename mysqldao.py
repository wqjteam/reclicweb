from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import pymysql

import pojo

conn = pymysql.Connect(
    host='2234p94b30.imdo.co',
    port=54833,
    user='root',
    passwd='123456',
    db='relic_data',
    charset='utf8'
)

engine = create_engine("mysql+pymysql://root:123456@192.168.4.110:3306/relic_data?charset=utf8")


def insert_history(search_data: pojo.SearchHistory):
    cursor = conn.cursor()
    sql_insert = search_data.get_insert_sql(cursor)
    cursor.execute(sql_insert)
    conn.commit()
    conn.close()
    cursor.close()
