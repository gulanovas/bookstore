from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, FloatField, IntegerField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisisasecret'
app.config['UPLOADED_IMAGES_DEST'] = 'static/images'


##CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books.db"
app.config['SQLALCHEMY_BINDS'] = {"user": "sqlite:///user.db"}
#Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class BookForm(FlaskForm):
    title = StringField('Book Title', validators=[DataRequired()])
    author = StringField('Book Author', validators=[DataRequired()])
    date = DateField('Book Date', validators=[DataRequired()])
    description = TextAreaField('Book Description', validators=[DataRequired()])
    img = FileField('Image', validators=[DataRequired()])
    trade_price = FloatField('Trade Price', validators=[DataRequired()])
    retail_price = FloatField('Retail Price', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])       
    submit = SubmitField('Submit')


##CREATE TABLE
class User(UserMixin, db.Model):
    __bind_key__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

##CREATE TABLE
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String, nullable=False)
    img = db.Column(db.String, nullable=False)
    trade_price = db.Column(db.Integer, nullable=False)
    retail_price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

db.create_all()


@app.route('/')
def home():
    return render_template("home.html", logged_in=current_user.is_authenticated)
    

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if User.query.filter_by(email=request.form.get('email')).first():
            #User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("store"))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
    
        user = User.query.filter_by(email=email).first()
        #Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('store'))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/store', methods=["GET", "POST"])
def store():
    ##READ ALL RECORDS
    all_books = db.session.query(Book).all()
    return render_template("store.html", books=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = BookForm()
    if form.validate_on_submit():
        # CREATE RECORD
        filename = "{}-{}".format(str(datetime.datetime.now()),secure_filename(form.img.data.filename))
        url = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
        form.img.data.save(url)
        new_book = Book(
            title = form.title.data,
            author = form.author.data,
            date = form.date.data,
     	    description = form.description.data,
            img = url,
            trade_price = form.trade_price.data,
            retail_price = form.retail_price.data,
            quantity = form.quantity.data
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('store'))
    return render_template("add.html", form=form)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        #UPDATE RECORD
        book_id = request.form["id"]
        book_to_update = Book.query.get(book_id)
        book_to_update.quantity = request.form["quantity"]
        db.session.commit()
        return redirect(url_for('store'))
    book_id = request.args.get('id')
    book_selected = Book.query.get(book_id)
    return render_template("edit.html", book=book_selected)


@app.route("/delete")
def delete():
    book_id = request.args.get('id')

    # DELETE A RECORD BY ID
    book_to_delete = Book.query.get(book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('store'))


@app.route("/cart")
def cart():
    return render_template('cart.html')


@app.route("/add_to_cart")
def add_to_cart():
    if request.method == "POST":
        filename = "{}-{}".format(str(datetime.datetime.now()),secure_filename(form.img.data.filename))
        url = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
        form.img.data.save(url)
        new_book = Book(
            title = form.title.data,
            author = form.author.data,
            date = form.date.data,
     	    description = form.description.data,
            img = url,
            trade_price = form.trade_price.data,
            retail_price = form.retail_price.data,
            quantity = form.quantity.data
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('cart'))
    return render_template('cart.html')


if __name__ == "__main__":
    app.run(debug=True)
