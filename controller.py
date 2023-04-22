from datetime import datetime

import click
from flask import Flask, render_template, request
from flask_cors import *

import service
from pojo import SearchHistoryPojo

app = Flask(__name__)


# the minimal Flask application
@app.route('/')
def index():
    return render_template('index.html',dataxxx='zheshi chuancanlede')


@app.route('/getAnswer', methods=['GET', 'POST'])
@cross_origin()
def getAnswerByQuestion():

    if request.method == 'POST':
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        question=request.form.get('question')
        ip=request.form.get('ip')
        insert_data=SearchHistoryPojo(mac_address=ip,search_data=question,insert_time=now,update_time=now)
        qa_result=service.search_data(insert_data)
        return qa_result
    else:
        return '不存在答案'



@app.route('/getfronthistory', methods=['GET', 'POST'])
@cross_origin()
def getFronthistory():

    if request.method == 'POST':

        ip=request.form.get('ip')
        insert_data=SearchHistoryPojo(mac_address=ip)
        returnjson=service.get_front_hinstory_data(insert_data)
        return returnjson
    else:
        return '不存在答案'



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