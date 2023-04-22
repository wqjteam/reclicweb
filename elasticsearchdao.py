from elasticsearch import Elasticsearch, helpers

es = Elasticsearch([{"host": "47.120.39.188", "port": 9200, "timeout": 1500}])


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


# 查询es
match_all_body = {
    "query": {
        "match_all": {

        }
    }
}
match_body = {
    "query": {

        "match": {

            "info": "春秋版画博物馆 北京"

        }
    }
}


def get_search_result(ner_result_arr):
    match_sentence = "info"
    match_sentence_relu = " ".join(ner_result_arr)
    match_body = {
        "query": {

            "match": {

                match_sentence: match_sentence_relu

            }
        }
    }
    return es.search(index="culture_heritage", body=match_body)
