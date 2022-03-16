from flask import render_template, Blueprint, request, redirect, url_for

main: Blueprint = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html', )