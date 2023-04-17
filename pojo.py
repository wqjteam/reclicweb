from datetime import datetime


class SearchHistory(object):
    def __int__(self,id,mac_address,search_data,audit,insert_time,update_time):
        self.id: int = id

        self.mac_address: str = mac_address

        self.search_data: str = search_data

        self.audit: str = audit

        self.insert_time: datetime = insert_time

        self.update_time: datetime = update_time

    def get_insert_sql(self):
        insertsql = "insert into search_history(macaddress,search_data,audit ,insert_time,update_time) values('%s','%s','%s','%s','%s')" \
                    % (self.mac_address, self.search_data, self.audit, self.insert_time, self.update_time)

        return insertsql

    def get_data_segment_page(self, condition, cursor):
        pass

