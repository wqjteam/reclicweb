import click
from flask import Flask, render_template, request

app = Flask(__name__)


# the minimal Flask application
@app.route('/')
def index():
    return render_template('index.html',dataxxx='zheshi chuancanlede')


@app.route('/getAnswer', methods=['GET', 'POST'])
# @app.route('/getAnswer/<question>')
def getAnswerByQuestion():

    if request.method == 'POST':
        question=request.form.get('question')
        print(question)
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
    app.run(port=5000,host="127.0.0.1",debug=True)