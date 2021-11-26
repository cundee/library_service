import csv, sqlite3
import pandas as pd

data = pd.read_csv('books.csv')

con = sqlite3.connect("library.db")

cur = con.cursor()

for i, row in data.iterrows():
    cur.execute("INSERT INTO books (id,book_name,publisher,author,publication_date,pages,isbn,description,link) VALUES (?,?,?,?,?,?,?,?,?);", tuple(row))
    con.commit()
con.close()