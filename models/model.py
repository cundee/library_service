from app import db

class Books(db.Model):
    __tablename__ = 'books'

    id                   = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True) 
    book_name            = db.Column(db.String(50), nullable=False)
    publisher            = db.Column(db.String(25), nullable=False)
    author               = db.Column(db.String(20), nullable=False)
    publication_date     = db.Column(db.Date, nullable=False)
    pages                = db.Column(db.Integer)
    isbn                 = db.Column(db.String(15), nullable=False)
    description          = db.Column(db.Text())
    link                 = db.Column(db.String(100), nullable=False)
    remain               = db.Column(db.Integer, nullable=False, default=5)


class User(db.Model):
    __tablename__ = 'user'

    id                   = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True) 
    user_id              = db.Column(db.String(50), nullable=False, unique=True)
    user_pw              = db.Column(db.String(255), nullable=False)
    nickname             = db.Column(db.String(20), nullable=False, unique=True)
    address              = db.Column(db.String(255), nullable=False)
    telephone            = db.Column(db.String(11), nullable=False)


class Rental(db.Model):
    __tablename__ = 'rental'

    id                   = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True) 
    user_id              = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id              = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    book_name            = db.Column(db.String(50), nullable=False)
    rental_date          = db.Column(db.Date, nullable=False)
    return_date          = db.Column(db.Date)

class Review(db.Model):
    __tablename__ = 'review'

    id                   = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True) 
    user_id              = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nickname             = db.Column(db.String(20), db.ForeignKey('user.nickname'), nullable=False)
    book_id              = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rating               = db.Column(db.Float, nullable=False)
    content              = db.Column(db.Text(), nullable=False)
    