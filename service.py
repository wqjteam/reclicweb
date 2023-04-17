import mysqldao
import pojo


def search_data(data: pojo.SearchHistory):
    mysqldao.insert_history(data)
    return "zhegshi fanhuishuju"