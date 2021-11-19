from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from sqlalchemy.sql.elements import Null
from models.model import *
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

bp = Blueprint('main',__name__,url_prefix='/')

# 메인페이지
@bp.route('/')
def home():
    book_list = Books.query.order_by(Books.id).all()
    return render_template('main.html',book_list=book_list)


# 회원가입
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


# 로그인
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

            flash(f"{user.nickname}님 어서오세요!")
            return redirect(url_for('main.home'))


# 로그아웃
@bp.route('/logout')
def logout():
    session.clear()
    flash("로그아웃")
    return redirect(url_for("main.home"))

# 책 상세정보
@bp.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Books.query.filter(Books.id==book_id).first()
    reviews = Review.query.filter(Review.book_id==book_id).all()

    if not book:
        flash("책 정보가 없습니다.")
        return redirect(url_for('main.home'))
    
    rating_sum = 0
    avg = 0
    if reviews:
        for review in reviews:
            rating_sum += review.rating
        avg = round(rating_sum / len(reviews))

    return render_template("detail.html",book=book,reviews=reviews,avg=avg)


@bp.route('/book/<int:book_id>', methods=['GET','POST'])
def rental_click(book_id):
    if request.method == 'GET':
        return render_template('detail.html')
    else:
        if session.get('login') is None:
            flash("먼저 로그인 해주세요")
            return redirect(url_for('main.login'))
        
        user = User.query.filter(User.id==session['login']).first()
        book = Books.query.filter(Books.id==book_id).first()
        rental_info = Rental.query.filter(Rental.user_id==user.id,Rental.book_id==book.id).first()
        remain = book.remain

        if remain == 0:
            flash("대출 가능한 책이 없습니다")
            return redirect(url_for("main.book_detail",book_id=book.id))
        elif rental_info:
            flash("이미 대출 중입니다")
            return redirect(url_for("main.book_detail",book_id=book.id))
        else:
            book.remain = remain - 1
            rental = Rental(user_id=user.id,book_id=book.id,book_name=book.book_name,rental_date=datetime.today())
            db.session.add(rental)
            db.session.commit()
            flash("책이 1권 대출되었습니다!")
            return render_template('detail.html',book=book)


# 반납하기
@bp.route('/return')
def my_return():
    if session.get('login') is None:
        flash("먼저 로그인 해주세요")
        return redirect(url_for('main.login'))
    
    items = Rental.query.filter(Rental.user_id==session['login'],Rental.return_date==None).all()
    return render_template('return.html',items=items)



@bp.route('/return/<int:book_id>', methods=['GET','POST'])
def return_click(book_id):
    if request.method == 'GET':
        return render_template('return.html')
    else:
        book = Books.query.filter(Books.id==book_id).first()
        rental_info = Rental.query.filter(Rental.user_id==session['login'],Rental.book_id==book.id).first()
        if rental_info:
            remain = book.remain
            book.remain = remain + 1
            rental_info.return_date = datetime.today()
            db.session.commit()
            flash("반납되었습니다")
            return redirect(url_for('main.my_return'))

# 대출기록
@bp.route('/record')
def my_record():
    if session.get('login') is None:
        flash("먼저 로그인 해주세요")
        return redirect(url_for('main.login'))
    
    rental_info = Rental.query.filter(Rental.user_id==session['login'],Rental.return_date!=None).all()
    return render_template("record.html", items=rental_info)
