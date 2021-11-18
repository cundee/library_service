from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from models.model import *
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('main',__name__,url_prefix='/')

@bp.route('/')
def home():
    book_list = Books.query.order_by(Books.id).all()
    return render_template('main.html',book_list=book_list)

@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        user_id   = request.form['user_id']
        user_pw   = request.form['user_pw']
        user_pw2  = request.form['user_pw2']
        nickname  = request.form['nickname']
        address   = request.form['address']
        telephone = request.form['telephone']
        
        user = User.query.filter(User.user_id == user_id).first()
        if user:
            flash("이미 가입된 아이디입니다.")
            return render_template('register.html')
        if user_pw != user_pw2:
            flash("비밀번호 확인이 일치하지 않습니다.") 
            return render_template('register.html')
        else:
            pw_hash = generate_password_hash(user_pw)
            user = User(user_id=user_id,user_pw=pw_hash,nickname=nickname,address=address,telephone=telephone)

            db.session.add(user)
            db.session.commit()

            flash("회원가입이 성공! 로그인 해주세요.")
            return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user_id         = request.form['user_id']
        user_pw         = request.form['user_pw']

        user = User.query.filter(User.user_id==user_id).first()

        if not user:
            flash("가입된 아이디가 존재하지 않습니다.")
            return render_template('login.html')
        if not check_password_hash(user.user_pw,user_pw):
            flash("비밀번호가 틀렸습니다.")
            return render_template('login.html')
        else:
            session.clear()
            session['login'] = user.id
            session['nickname'] = user.nickname

            flash(f"{user.nickname}님 어서오세요!")
            return redirect(url_for('main.home'))

@bp.route('/logout')
def logout():
    session.clear()
    flash("로그아웃")
    return redirect(url_for("main.home"))

