from flask import render_template
from app import app


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Roman'}
    posts = [
        {
            'author': {'username': 'Ivan'},
            'body': 'Beautiful day in Moscow!'
        },
        {
            'author': {'username': 'Stepan'},
            'body': 'The Fallout movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)