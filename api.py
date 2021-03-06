from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from sqlalchemy.sql.elements import *
from models.model import *
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta,date
import re

bp = Blueprint('main',__name__,url_prefix='/')

# 메인페이지
@bp.route('/')
def home():
    kw = request.args.get('kw',type=str,default='')
    if kw:
        search = '%%{}%%'.format(kw)
        book_list = Books.query.filter(Books.book_name.like(search)).order_by(Books.id).all()
    else:
        book_list = Books.query.order_by(Books.id).all()
    return render_template('main.html',book_list=book_list,kw=kw)
    

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
        if re.search(r'\W',user_pw) is None:
            none_cnt += 1
        
        if ((none_cnt==0 and len(user_pw)>=8) or (none_cnt==1 and len(user_pw)>=10)) is not True:
            flash("영어문자, 숫자, 특수문자 중 2종류 이상 사용하여 최소 8자 이상 입력하세요.")
            return render_template('register.html',user_id=user_id,user_pw=user_pw,user_pw2=user_pw2,nickname=nickname,address=address,telephone=telephone)
        if user:
            flash("이미 가입된 아이디입니다.")
            return render_template('register.html',user_id=user_id,user_pw=user_pw,user_pw2=user_pw2,nickname=nickname,address=address,telephone=telephone)
        if user_pw != user_pw2:
            flash("비밀번호 확인이 일치하지 않습니다.") 
            return render_template('register.html',user_id=user_id,user_pw=user_pw,user_pw2=user_pw2,nickname=nickname,address=address,telephone=telephone)
        if nickname_:
            flash("이미 사용중인 닉네임입니다.")
            return render_template('register.html',user_id=user_id,user_pw=user_pw,user_pw2=user_pw2,nickname=nickname,address=address,telephone=telephone)
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
        
        today = date.today()
        user = User.query.filter(User.id==session['login']).first()
        book = Books.query.filter(Books.id==book_id).first()
        rental_info = Rental.query.filter(Rental.user_id==user.id,Rental.book_id==book.id,Rental.return_date==None).first()
        late_info = Rental.query.filter(Rental.user_id==user.id,Rental.return_due_date<today,Rental.return_date==None).first()
        remain = book.remain

        if remain == 0:
            flash("대출 가능한 책이 없습니다")
            return redirect(url_for("main.book_detail",book_id=book.id))
        elif rental_info:
            flash("이미 대출 중입니다")
            return redirect(url_for("main.book_detail",book_id=book.id))
        elif (user.late_fee!=0) or (late_info):
            flash("대출중인 책 중에 연체된 도서가 있습니다. 도서를 반납하고 연체료를 지불해주세요.")
            return redirect(url_for("main.book_detail",book_id=book.id))
        else:
            book.remain = remain - 1
            date_today = date.today()
            return_due_date = date_today + timedelta(days=15)
            rental = Rental(user_id=user.id,book_id=book.id,book_name=book.book_name,rental_date=date_today, return_due_date=return_due_date)
            db.session.add(rental)
            db.session.commit()
            flash("책이 1권 대출되었습니다!")
            return redirect(url_for("main.book_detail",book_id=book.id))

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
        review = Review(user_id=user.id,book_id=book_id,nickname=user.nickname,rating=rating,content=content,date=date.today())
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

# 반납하기 페이지
@bp.route('/return')
def my_return():
    if session.get('login') is None:
        flash("먼저 로그인 해주세요")
        return redirect(url_for('main.login'))
    user = User.query.filter(User.id==session['login']).first()
    items = Rental.query.filter(Rental.user_id==session['login'],Rental.return_date==None).all()
    today = date.today()
    return render_template('return.html',items=items,user=user,today=today)
        

# 반납하기 클릭
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
            today = date.today()
            rental_info.return_date = today

            if rental_info.return_due_date < today:
                date_diff = today - rental_info.return_due_date
                diff = date_diff.days
                user = User.query.filter(User.id==session['login']).first()
                user.late_fee += diff*100
                db.session.commit()
                flash("연체료가 발생하였습니다. 연체료 지불 후 대출이 가능합니다.")
                return redirect(url_for('main.my_return'))
            
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
