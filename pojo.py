from datetime import datetime


class SearchHistory:
    def __int__(self):
        self.id: int = None

        self.macaddress: str = None

        self.search_data: str = None

        self.audit: str = None

        self.insert_time: datetime = None

        self.update_time: datetime = None

    def get_insert_sql(self):
        insertsql = "insert into search_history(macaddress,search_data,audit ,insert_time,update_time) values('%s','%s','%s','%s','%s')" \
                    % (self.macaddress, self.search_data, self.audit, self.insert_time, self.update_time)

        return insertsql

    def get_data_segment_page(self, condition, cursor):
        pass

