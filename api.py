from operator import add
from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from sqlalchemy.sql.elements import *
from models.model import *
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import re

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
        nickname_ = User.query.filter(User.nickname==nickname).first()

        none_cnt = 0
        if re.search(r'[0-9]',user_pw) is None:
            none_cnt += 1
        if re.search(r'[a-zA-Z]',user_pw) is None:
            none_cnt += 1
        if re.search('\W',user_pw) is None:
            none_cnt += 1
        
        # 3종류 & 8자 이상
        # 2종류 & 10자 이상
        if ((none_cnt==0 and len(user_pw)>=8) or (none_cnt==1 and len(user_pw)>=10)) is not True:
            flash("영어문자, 숫자, 특수문자 중 2종류 이상 사용하여 최소 8자 이상 입력하세요.")
            return render_template('register.html')
        if user:
            flash("이미 가입된 아이디입니다.")
            return render_template('register.html')
        if user_pw != user_pw2:
            flash("비밀번호 확인이 일치하지 않습니다.") 
            return render_template('register.html')
        if nickname_:
            flash("이미 사용중인 닉네임입니다.")
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
    count = len(reviews)
    if not book:
        flash("책 정보가 없습니다.")
        return redirect(url_for('main.home'))

    return render_template("detail.html",book=book,reviews=reviews,count=count)

# 대출하기
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
        rental_info = Rental.query.filter(Rental.user_id==user.id,Rental.book_id==book.id,Rental.return_date==None).first()
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

# 리뷰작성
@bp.route('/book/write/<int:book_id>', methods=['POST'])
def review_update(book_id):
    user = User.query.filter(User.id==session['login']).first()
    rental_record = Rental.query.filter(Rental.user_id==user.id,Rental.book_id==book_id).first()
    if not rental_record:
        flash("책을 이용한 이용자에게만 작성 권한이 주어집니다.")
        return redirect(url_for('main.book_detail', book_id=book_id))
    else:
        rating = request.form['star']
        content = request.form['content']
        
        reviews = Review.query.filter(Review.book_id==book_id).all()
        book = Books.query.filter(Books.id==book_id).first()
        rating_sum = int(rating)
        star_avg = rating
        if reviews:
            for review in reviews:
                rating_sum += review.rating
            star_avg = round(rating_sum / (len(reviews)+1))

        book.star = star_avg
        review = Review(user_id=user.id,book_id=book_id,nickname=user.nickname,rating=rating,content=content,date=datetime.today())
        db.session.add(review)
        db.session.commit()
        
        flash('리뷰가 등록되었습니다.')
        return redirect(url_for('main.book_detail',book_id=book_id))
# 리뷰삭제
@bp.route('/book/delete/<int:review_id>')
def review_delete(review_id):
    deleted_review = Review.query.filter(Review.id==review_id).first()
    reviews = Review.query.filter(Review.book_id==deleted_review.book_id).all()
    book = Books.query.filter(Books.id==deleted_review.book_id).first()

    rating_sum = 0
    if reviews:
        for review in reviews:
            if review.id != review_id:
                rating_sum += review.rating
        if len(reviews) == 1:
            star_avg = 0
        else:
            star_avg = round(rating_sum / (len(reviews)-1))

    book.star = star_avg
    db.session.delete(deleted_review)
    db.session.commit()
    flash('리뷰가 삭제되었습니다.')
    return redirect(url_for('main.book_detail',book_id=book.id))

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
        rental_info = Rental.query.filter(Rental.user_id==session['login'],Rental.book_id==book.id,Rental.return_date==None).first()
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
