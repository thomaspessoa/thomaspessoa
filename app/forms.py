from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
from flask_babel import lazy_gettext as _l

class RegistrationForm(FlaskForm):
    username = StringField(_l('Nome de usuário'), validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Senha'), validators=[DataRequired()])
    confirm_password = PasswordField(_l('Confirmar Senha'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Registrar'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_l('Este nome de usuário já está em uso. Por favor, escolha outro.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_l('Este email já está em uso. Por favor, escolha outro.'))

class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Senha'), validators=[DataRequired()])
    remember = BooleanField(_l('Lembrar-me'))
    submit = SubmitField(_l('Entrar'))

class ProductForm(FlaskForm):
    title = StringField(_l('Título'), validators=[DataRequired()])
    description = TextAreaField(_l('Descrição'), validators=[DataRequired()])
    price = FloatField(_l('Preço'), validators=[DataRequired()])
    city = SelectField(_l('Cidade'), choices=[('Santa Maria', 'Santa Maria'), ('Nova Palma', 'Nova Palma'), ('Agudo', 'Agudo'), ('Restinga Seca', 'Restinga Seca')], validators=[DataRequired()])
    picture = FileField(_l('Foto do Produto'), validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField(_l('Anunciar Produto'))
