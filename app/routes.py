import os
from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from app import db, bcrypt
from app.models import User, Product
from app.forms import RegistrationForm, LoginForm, ProductForm
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from flask_babel import lazy_gettext as _l

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    query = request.args.get('query')
    city = request.args.get('city')
    products_query = Product.query

    if query:
        products_query = products_query.filter(Product.title.contains(query) | Product.description.contains(query))

    if city:
        products_query = products_query.filter_by(city=city)

    products = products_query.all()
    return render_template('index.html', products=products)

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(_l('Sua conta foi criada! Agora você pode fazer login'), 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title=_l('Registrar'), form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash(_l('Login sem sucesso. Por favor, verifique o email e a senha'), 'danger')
    return render_template('login.html', title=_l('Entrar'), form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

def save_picture(form_picture):
    random_hex = os.urandom(8).hex()
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads', picture_fn)

    # Create the uploads directory if it doesn't exist
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)

    form_picture.save(picture_path)
    return picture_fn

@main.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            product = Product(title=form.title.data, description=form.description.data, price=form.price.data, city=form.city.data, image_file=picture_file, author=current_user)
        else:
            product = Product(title=form.title.data, description=form.description.data, price=form.price.data, city=form.city.data, author=current_user)
        db.session.add(product)
        db.session.commit()
        flash(_l('Seu produto foi anunciado!'), 'success')
        return redirect(url_for('main.home'))
    return render_template('create_listing.html', title=_l('Novo Produto'), form=form, legend=_l('Novo Produto'))

@main.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', title=product.title, product=product)
