import os
import secrets
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, ProductForm, RatingForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/product_pics'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Ensure the upload folder exists
try:
    os.makedirs(app.config['UPLOAD_FOLDER'])
except OSError:
    pass


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    products = db.relationship('Product', backref='author', lazy=True)
    ratings_given = db.relationship('Rating', foreign_keys='Rating.buyer_id', backref='buyer', lazy=True)
    ratings_received = db.relationship('Rating', foreign_keys='Rating.seller_id', backref='seller', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def average_rating(self):
        if not self.ratings_received:
            return 0
        return sum(r.stars for r in self.ratings_received) / len(self.ratings_received)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    is_sold = db.Column(db.Boolean, nullable=False, default=False)
    phone_number = db.Column(db.String(20), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ratings = db.relationship('Rating', backref='product', lazy=True)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


@app.route("/")
@app.route("/home")
def home():
    search_query = request.args.get('search')
    if search_query:
        products = Product.query.filter(or_(Product.title.contains(search_query), Product.description.contains(search_query))).all()
    else:
        products = Product.query.all()
    return render_template('home.html', products=products, search_query=search_query)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Sua conta foi criada! Agora você pode fazer login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Cadastrar', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login sem sucesso. Por favor, verifique seu email e senha.', 'danger')
    return render_template('login.html', title='Entrar', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], picture_fn)

    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/product/new", methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)
        product = Product(title=form.title.data,
                          description=form.description.data,
                          price=form.price.data,
                          phone_number=form.phone_number.data,
                          image_file=picture_file,
                          author=current_user)
        db.session.add(product)
        db.session.commit()
        flash('Seu produto foi anunciado!', 'success')
        return redirect(url_for('home'))
    return render_template('add_product.html', title='Novo Produto',
                           form=form, legend='Novo Produto')


@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    form = RatingForm()
    return render_template('product.html', title=product.title, product=product, form=form)


@app.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
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
        db.session.commit()
        flash('Seu produto foi atualizado!', 'success')
        return redirect(url_for('product', product_id=product.id))
    elif request.method == 'GET':
        form.title.data = product.title
        form.description.data = product.description
        form.price.data = product.price
        form.phone_number.data = product.phone_number
    return render_template('add_product.html', title='Atualizar Produto',
                           form=form, legend='Atualizar Produto')


@app.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Seu produto foi excluído!', 'success')
    return redirect(url_for('home'))


@app.route("/product/<int:product_id>/sold", methods=['POST'])
@login_required
def mark_sold(product_id):
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        abort(403)
    product.is_sold = True
    db.session.commit()
    flash('Seu produto foi marcado como vendido!', 'success')
    return redirect(url_for('product', product_id=product.id))


@app.route("/rate_seller/<int:product_id>", methods=['POST'])
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
    return redirect(url_for('product', product_id=product.id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
