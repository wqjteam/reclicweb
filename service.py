from datetime import datetime
import json

import mysqldao
import pojo


def search_data(data: pojo.SearchHistoryPojo):
    mysqldao.insert_history(data)
    return "zhegshi fanhuishuju"


def get_front_hinstory_data(data: pojo.SearchHistoryPojo):
    returndata= mysqldao.get_history_front_data(data)
    returnjosnstr=json.dumps(returndata, cls=DateEncoder,ensure_ascii=False)
    return returnjosnstr


def get_backward_hinstory_data(mac_address, index, rows):
    mysqldao.get_history_backward_data(mac_address, index, rows)
    return "zhegshi fanhuishuju"


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)