from datetime import datetime

import click
from flask import Flask, render_template, request
from flask_cors import *

import service
from pojo import SearchHistoryPojo, AdminPojo

app = Flask(__name__)


# the minimal Flask application


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


@app.route('/login', methods=['GET', 'POST'])
@cross_origin()
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    loginData = AdminPojo(username=username, password=password)
    id = service.get_backward_login(loginData)
    if id >= 0:
        return "登陆成功||" + str(id) + "||" + username
    else:
        return "账号或者密码有误"


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
    if username is None or id is None:
        return render_template('backwardlogin.html')
    else:
        return render_template('backwardindex.html', username=username, id=id)


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
