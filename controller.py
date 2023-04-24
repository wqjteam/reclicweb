from datetime import datetime

import click
from flask import Flask, render_template, request
from flask_cors import *

import pojo
import service
from pojo import SearchHistoryPojo, AdminPojo

app = Flask(__name__)

# the minimal Flask application


"""
用户相关
"""


@app.route('/login', methods=['GET', 'POST'])
@cross_origin()
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    loginData = AdminPojo(username=username, password=password)
    word_no = service.get_backward_login(loginData)
    if word_no !="-1":
        return "登陆成功||" + str(word_no[0][0]) + "||" + username+"||"+word_no[0][1]
    else:
        return "账号或者密码有误"


@app.route('/updateadminself', methods=['GET', 'POST'])
@cross_origin()
def updateadminself():
    id = request.form.get('id')
    work_no = request.form.get('work_no')
    password = request.form.get('password')
    username = request.form.get('username')

    return service.update_admin_self(id=id, username=username, password=password, work_no=work_no)


@app.route('/adminpage', methods=['GET', 'POST'])
@cross_origin()
def adminpage():
    work_no = request.form.get('work_no')
    pageindex = request.form.get('pageindex')

    return service.get_admin_page(work_no, pageindex)


@app.route('/adminresetpassword', methods=['GET', 'POST'])
@cross_origin()
def adminresetpassword():
    id = request.form.get('id')
    password = request.form.get('password')
    return service.update_admin_password(id=id)


@app.route('/adminaudit', methods=['GET', 'POST'])
@cross_origin()
def adminaudit():
    id = request.form.get('id')
    status = request.form.get('status')
    return service.admin_audit(id=id, audit=status)


@app.route('/createadmin', methods=['GET', 'POST'])
@cross_origin()
def createadmin():
    jsondata = request.json
    username = jsondata.get('username')
    password = jsondata.get('password')
    work_no = jsondata.get('work_no')

    return service.create_admin(username, password, work_no)


"""
文章相关
"""


@app.route('/searchBackwardpassage', methods=['GET', 'POST'])
@cross_origin()
def searchBackwardpassage():
    search_data = request.form.get('passage_content')
    pageNo = request.form.get('pageNo')

    data = service.get_passage_audit_page(blurcontent=search_data, pageindex=int(pageNo))
    return data


@app.route('/passageaudit', methods=['GET', 'POST'])
@cross_origin()
def passageaudit():
    if request.method == 'POST':

        id = request.form.get('id')
        es_id = request.form.get('es_id')
        audit = request.form.get('audit')
        # create_time = request.form.get('create_time')
        # update_time = request.form.get('update_time')
        insert_data = pojo.PassageAudit(id=id, es_id=es_id, audit=audit)
        returnjson = service.insert_update_audit_passage(insert_data)
        return returnjson
    else:
        return '不存在答案'


"""
搜索记录相关
"""


@app.route('/getAnswer', methods=['GET', 'POST'])
@cross_origin()
def getAnswerByQuestion():
    if request.method == 'POST':
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        question = request.form.get('question')
        ip = request.form.get('ip')
        insert_data = SearchHistoryPojo(mac_address=ip, search_data=question, insert_time=now, update_time=now)
        qa_result = service.search_data(insert_data)
        return qa_result
    else:
        return '不存在答案'


@app.route('/getfronthistory', methods=['GET', 'POST'])
@cross_origin()
def getFronthistory():
    if request.method == 'POST':

        ip = request.form.get('ip')
        insert_data = SearchHistoryPojo(mac_address=ip)
        returnjson = service.get_front_history_data(insert_data)
        return returnjson
    else:
        return '不存在答案'


@app.route('/searchBackwardHistory', methods=['GET', 'POST'])
@cross_origin()
def searchBackwardHistory():
    search_data = request.form.get('username')
    pageNo = request.form.get('pageNo')
    ip = request.form.get('ip')

    data = service.get_backward_history_data(mac_address=ip, search_data=search_data, index=pageNo)
    return data


@app.route('/searchupdate', methods=['GET', 'POST'])
@cross_origin()
def searchupdate():
    id = request.form.get('id')
    audit = request.form.get('audit')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data = service.update_history_data(id, now, audit)
    return data


"""
界面跳转
"""


@app.route('/')
@app.route('/index')
@cross_origin()
def index():
    return render_template('index.html', dataxxx='zheshi chuancanlede')


@app.route('/tologinback', methods=['GET', 'POST'])
@cross_origin()
def tologinback():
    return render_template('backwardlogin.html')


@app.route('/backwardindex', methods=['GET', 'POST'])
@cross_origin()
def backwardindex():
    username = request.args.get('username')
    id = request.args.get('id')
    workno = request.args.get('workno')
    if username is None or id is None:
        return render_template('backwardlogin.html')
    else:
        return render_template('backwardindex.html', username=username, id=id,workno=workno)


@app.route('/aduithistory', methods=['GET', 'POST'])
@cross_origin()
def aduithistory():
    username = request.args.get('username')
    id = request.args.get('id')
    if username is None or id is None:
        return render_template('backwardlogin.html')
    else:
        return render_template('aduithistory.html')


@app.route('/aduitpassage', methods=['GET', 'POST'])
@cross_origin()
def aduitpassage():
    username = request.args.get('username')
    id = request.args.get('id')
    if username is None or id is None:
        return render_template('backwardlogin.html')
    else:
        return render_template('aduitpassage.html')


@app.route('/peoplemanage', methods=['GET', 'POST'])
@cross_origin()
def peoplemanage():
    username = request.args.get('username')
    id = request.args.get('id')
    if username is None or id is None:
        return render_template('backwardlogin.html')
    else:
        return render_template('peoplemanage.html')


@app.route('/logout', methods=['GET', 'POST'])
@cross_origin()
def logout():
    return render_template('backwardlogin.html')


# bind multiple URL for one view function
@app.route('/hi')
@app.route('/hello')
def say_hello():
    print('say_hello')
    return '<h1>Hello, Flask!</h1>'


# dynamic route, URL variable default
@app.route('/greet', defaults={'name': 'Programmer'})
@app.route('/greet/<name>')
def greet(name):
    return '<h1>Hello, %s!</h1>' % name


# custom flask cli command
@app.cli.command()
def hello():
    """Just say hello."""
    click.echo('Hello, Human!')


if __name__ == '__main__':
    pass
