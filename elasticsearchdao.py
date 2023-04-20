import pymysql
from sqlalchemy import create_engine
# from sqlalchemy.dialects.mysql import pymysql
from elasticsearch import Elasticsearch, helpers
import pojo

conn = pymysql.Connect(
    host='47.120.39.188',
    port=3306,
    user='root',
    passwd='qwertyuiop123456',
    db='relic_data',
    charset='utf8'
)
cursor = conn.cursor()
engine = create_engine("mysql+pymysql://root:123456@192.168.4.110:3306/relic_data?charset=utf8")


def read_es(host, port, index, query=""):
    url = {"host": host, "port": port, "timeout": 1500}

    es = Elasticsearch([url])
    if es.ping():
        print("Successfully connect!")
    else:
        print("Failed.....")
        exit()
    if query == "":  # query为es的搜索条件
        query = {
            "query": {
                "match_all": {}
            },
            # "size":1000
        }
    res = helpers.scan(es, index=index, scroll="20m", query=query)
    return res


from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def write_es(host, port, index, query=""):
    es = Elasticsearch([{"host": host, "port": port, "timeout": 1500}])

    ACTIONS = []
    action1 = {
        "_index": "indes_test",
        "_type": "doc_type_test",
        "_id": "bSlegGUBmJ2C8ZCSC1R1",
        "_source": {
            "id": "1111122222",
            "serial": "版本",
            "tags.content": "标签2",
            "tags.dominant_color_name": "域名的颜色黄色",
            "tags.skill": "分类信息",
            "hasTag": "123",
            "status": "11",
            "createTime": "2018-2-2",
            "updateTime": "2018-2-3",
        }
    }
    action2 = {
        "_index": "indes_test",
        "_type": "doc_type_test",
        "_id": "bSlegGUBmJ2C8ZCSC1R2",
        "_source": {
            "id": "1111122222",
            "serial": "版本",
            "tags.content": "标签2",
            "tags.dominant_color_name": "域名的颜色黄色",
            "tags.skill": "分类信息",
            "hasTag": "123",
            "status": "11",
            "createTime": "2018-2-2",
            "updateTime": "2018-2-3",
        }
    }

    ACTIONS.append(action1)
    ACTIONS.append(action2)

    res, _ = bulk(es, ACTIONS, index="indes_test", raise_on_error=True)
    print(res)


data = read_es('47.120.39.188', 9200, "fasss.index", query="")
