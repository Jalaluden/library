from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.secret_key = 'secret_key'
db = SQLAlchemy(app)
app.app_context().push()

from models import Book, Member, Transaction

@app.route('/')
def home():
    books = Book.query.all()
    members = Member.query.all()
    return render_template('index.html', books=books, members=members)


@app.route('/book/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        stock = int(request.form['stock'])
        book = Book(title=title, author=author, stock=stock)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect('/')
    return render_template('add_book.html')


@app.route('/member/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        member = Member(name=name)
        db.session.add(member)
        db.session.commit()
        flash('Member added successfully!', 'success')
        return redirect('/')
    return render_template('add_member.html')


@app.route('/book/<int:book_id>/issue', methods=['GET', 'POST'])
def issue_book(book_id):
    book = Book.query.get(book_id)
    if request.method == 'POST':
        member_id = int(request.form['member_id'])
        member = Member.query.get(member_id)
        if book.stock > 0:
            book.stock -= 1
            transaction = Transaction(book_id=book_id, member_id=member_id, issue_date=datetime.date.today())
            db.session.add(transaction)
            db.session.commit()
            flash(f'Book "{book.title}" issued to {member.name} successfully!', 'success')
            return redirect('/')
        else:
            flash('Book is out of stock!', 'error')
    members = Member.query.all()
    return render_template('issue_book.html', book=book, members=members)


@app.route('/book/<int:book_id>/return', methods=['GET', 'POST'])
def return_book(book_id):
    book = Book.query.get(book_id)
    if request.method == 'POST':
        member_id = int(request.form['member_id'])
        member = Member.query.get(member_id)
        transaction = Transaction.query.filter_by(book_id=book_id, member_id=member_id, return_date=None).first()
        if transaction:
            transaction.return_date = datetime.date.today()
            days_rented = (transaction.return_date - transaction.issue_date).days
            transaction.rent_fee = calculate_rent_fee(days_rented)
            member.outstanding_debt += transaction.rent_fee
            book.stock += 1
            db.session.commit()
            flash(f'Book "{book.title}" returned by {member.name} successfully!', 'success')
            return redirect('/')
        else:
            flash('Book is not issued to the selected member!', 'error')
    members = Member.query.all()
    return render_template('return_book.html', book=book, members=members)


@app.route('/search', methods=['GET', 'POST'])
def search_books():
    if request.method == 'POST':
        search_query = request.form['search_query']
        books = Book.query.filter(
            (Book.title.contains(search_query)) | (Book.author.contains(search_query))
        ).all()
        return render_template('search_results.html', books=books)
    return render_template('search_books.html')


def calculate_rent_fee(days_rented):
    # Implement your logic to calculate the rental fee here
    return days_rented * 10.0  # Example: Rs. 10 per day


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
