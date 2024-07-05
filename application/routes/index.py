from flask import Flask, render_template, redirect, url_for, flash, Blueprint

index_bp = Blueprint('index', __name__)


@index_bp.route('/index')
def index():
    return render_template('index.html')
