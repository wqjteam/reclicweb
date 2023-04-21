
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch([{"host": "47.120.39.188", "port": 3306, "timeout": 1500}])


def read_es(host, port, index, query=""):
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






data = read_es('47.120.39.188', 9200, "fasss.index", query="")

# 查询es
body = {
    "query":{
        "match_all":{}
    }
}
es.search(index="culture_heritage" ,body=body)