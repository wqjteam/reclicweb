from datetime import datetime

import click
from flask import Flask, render_template, request
from flask_cors import *

from pojo import SearchHistory
from service import search_data

app = Flask(__name__)


# the minimal Flask application
@app.route('/')
def index():
    return render_template('index.html',dataxxx='zheshi chuancanlede')


@app.route('/getAnswer', methods=['GET', 'POST'])
# @app.route('/getAnswer/<question>')
@cross_origin()
def getAnswerByQuestion():

    if request.method == 'POST':
        now=datetime.now().strftime('%Y-%m-%d_%H%M%S')
        question=request.form.get('question')
        ip=request.form.get('ip')
        insert_data=SearchHistory(mac_address=ip,search_data=question,audit=0,insert_time=now,update_time=now)
        search_data(insert_data)
        return 'question=== %s!hahah' % question
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