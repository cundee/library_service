from flask import Blueprint, render_template
from models.model import *

bp = Blueprint('main',__name__,url_prefix='/')

@bp.route('/')
def home():
    book_list = Books.query.order_by(Books.book_name).all()
    return render_template('index.html',book_list=book_list)
