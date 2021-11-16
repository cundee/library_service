from app import db

class Books(db.Model):
    __tablename__ = 'books'

    id                   = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True) 
    book_name            = db.Column(db.String(50), nullable=False)
    publisher            = db.Column(db.String(25))
    author               = db.Column(db.String(20))
    publication_date     = db.Column(db.Date)
    pages                = db.Column(db.Integer)
    isbn                 = db.Column(db.String(15), nullable=False)
    describe_option      = db.Column(db.Text)
    link                 = db.Column(db.String(100), nullable=False)

    