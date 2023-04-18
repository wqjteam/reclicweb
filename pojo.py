from datetime import datetime


class SearchHistoryPojo():
    def __init__(self, id=0, mac_address=None, search_data=None, audit="0", insert_time=None, update_time=None):
        self.id: int = id

        self.mac_address: str = mac_address

        self.search_data: str = search_data

        self.audit: str = audit

        self.insert_time: datetime = insert_time

        self.update_time: datetime = update_time

    def get_insert_sql(self):
        insertsql = "insert into relic_data.search_history(macaddress,search_data,audit ,insert_time,update_time) values('%s','%s','%s','%s','%s')" \
                    % (self.mac_address, self.search_data, self.audit, self.insert_time, self.update_time)

        return insertsql

    # 只可以查询自己额历史记录
    def get_front_history_sql(self):
        returnsql = self.get_data_segment_page(mac_address=self.mac_address,
                                               audit=1) + " order by update_time desc limit 10"
        return returnsql

    def get_backword_history_sql_page(self, mac_address, search_data, index, rows):

        return self.get_data_segment_page(mac_address=mac_address, search_data=search_data, audit=0, pagerows=rows,
                                          pageindex=index)

    def get_data_segment_page(self, mac_address=None, search_data=None, audit=None, pagerows: int = None,
                              pageindex: int = None):
        selectsql = "select id,macaddress,search_data,audit,insert_time,update_time from  relic_data.search_history where 1=1"
        if mac_address is not None:
            selectsql = selectsql + " and   macaddress='" + mac_address + "'"

        if search_data is not None:
            selectsql = selectsql + " and   search_data  like'%" + search_data + "%'"

        # 前端查询查  0 默认 可以显示，-1是被否决的 ，1是可以显示的
        if audit is not None:
            if audit == 1:

                # 前端查询 查  0 默认 可以显示，-1是被否决的 ，1是可以显示的
                selectsql = selectsql + " and (audit='0' or audit='1' ) "
            else:
                # 后端查询
                selectsql = selectsql + " and  audit='0')"

        if pagerows is not None and pageindex is not None:
            selectsql = selectsql + " limit %d,%d" % ((pageindex - 1) * pagerows, pageindex * pagerows)
        return selectsql
