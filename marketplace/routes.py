import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, current_app
from flask_login import login_user, current_user, logout_user, login_required
from marketplace import db
from marketplace.models import User, Product, Rating
from marketplace.forms import RegistrationForm, LoginForm, ProductForm, RatingForm

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    search_query = request.args.get('search')
    city_filter = request.args.get('city')
    query = Product.query
    if search_query:
        query = query.filter(db.or_(Product.title.contains(search_query), Product.description.contains(search_query)))
    if city_filter:
        query = query.filter(Product.city == city_filter)
    products = query.all()
    return render_template('home.html', products=products, search_query=search_query, city_filter=city_filter)


@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Sua conta foi criada! Agora você pode fazer login.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Cadastrar', form=form)


@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login sem sucesso. Por favor, verifique seu email e senha.', 'danger')
    return render_template('login.html', title='Entrar', form=form)


@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/product_pics', picture_fn)

    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@main.route("/product/new", methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)
        product = Product(title=form.title.data,
                          description=form.description.data,
                          price=form.price.data,
                          phone_number=form.phone_number.data,
                          city=form.city.data,
                          image_file=picture_file,
                          author=current_user)
        db.session.add(product)
        db.session.commit()
        flash('Seu produto foi anunciado!', 'success')
        return redirect(url_for('main.home'))
    return render_template('add_product.html', title='Novo Produto',
                           form=form, legend='Novo Produto')


@main.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    form = RatingForm()
    return render_template('product.html', title=product.title, product=product, form=form)


@main.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            product.image_file = picture_file
        product.title = form.title.data
        product.description = form.description.data
        product.price = form.price.data
        product.phone_number = form.phone_number.data
        product.city = form.city.data
        db.session.commit()
        flash('Seu produto foi atualizado!', 'success')
        return redirect(url_for('main.product', product_id=product.id))
    elif request.method == 'GET':
        form.title.data = product.title
        form.description.data = product.description
        form.price.data = product.price
        form.phone_number.data = product.phone_number
        form.city.data = product.city
    return render_template('add_product.html', title='Atualizar Produto',
                           form=form, legend='Atualizar Produto')


@main.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Seu produto foi excluído!', 'success')
    return redirect(url_for('main.home'))


@main.route("/product/<int:product_id>/sold", methods=['POST'])
@login_required
def mark_sold(product_id):
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        abort(403)
    product.is_sold = True
    db.session.commit()
    flash('Seu produto foi marcado como vendido!', 'success')
    return redirect(url_for('main.product', product_id=product.id))


@main.route("/rate_seller/<int:product_id>", methods=['POST'])
@login_required
def rate_seller(product_id):
    product = Product.query.get_or_404(product_id)
    form = RatingForm()
    if form.validate_on_submit():
        rating = Rating(stars=form.stars.data,
                        comment=form.comment.data,
                        buyer=current_user,
                        seller=product.author,
                        product=product)
        db.session.add(rating)
        db.session.commit()
        flash('Sua avaliação foi enviada!', 'success')
    return redirect(url_for('main.product', product_id=product.id))
