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

    def audit_history_sql(self, history_id, audit_status=0):
        update_password_sql = "update relic_data.search_history set audit='%s' where id='%d'" % (
            audit_status, history_id)
        return update_password_sql


class AdminPojo():
    def __init__(self, id=0, username=None, password=None, work_no=None, create_time=None, update_time=None):
        self.id: int = id

        self.username: str = username

        self.password: str = password

        self.work_no: str = work_no

        self.create_time: datetime = create_time

        self.update_time: datetime = update_time

    def get_register_pre_sql(self):
        insert_pre_sql = "select count(1) from relic_data.admin where work_no='%s' " % self.work_no

        return insert_pre_sql

    def get_register_sql(self):
        insertsql = "insert into relic_data.admin(username,password,work_no ,create_time,update_time) values('%s','%s','%s','%s','%s')" \
                    % (self.username, self.password, self.work_no, self.create_time, self.update_time)

        return insertsql

    def get_update_password_pre_sql(self):
        update_password_pre_sql = "select id from relic_data.admin where username='%s' and work_no='%s' " % (
            self.username, self.work_no)
        return update_password_pre_sql

    def get_update_password_sql(self):
        update_password_sql = "update relic_data.admin set password='%s' where work_no='%s'" % (
            self.password, self.work_no)
        return update_password_sql

    def get_login_sql(self):
        login_sql = "select id from  relic_data.admin where username='%s' and password='%s'" % (
            self.username, self.password)
        return login_sql


class PassageAudit():
    def __init__(self, id=0, es_id=None, audit=0, create_time=None, update_time=None):
        self.id: int = id

        self.es_id: str = es_id

        self.audit: str = audit

        self.create_time: datetime = create_time

        self.update_time: datetime = update_time

    def get_insert_sql(self):
        insert_sql = "insert  into relic_data.passage_audit(es_id,audit ,create_time,update_time) values('%s','%s','%s','%s')" % (
            self.es_id, self.audit, self.create_time, self.update_time
        )

        return insert_sql
