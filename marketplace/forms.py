from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, RadioField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from marketplace.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Nome de usuário',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Cadastrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está em uso. Por favor, escolha outro.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')


class ProductForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    price = FloatField('Preço', validators=[DataRequired()])
    phone_number = StringField('Telefone (WhatsApp)', validators=[DataRequired()])
    city = SelectField('Cidade', choices=[('Restinga Sêca', 'Restinga Sêca'), ('Agudo', 'Agudo'), ('Nova Palma', 'Nova Palma'), ('Santa Maria', 'Santa Maria')], validators=[DataRequired()])
    picture = FileField('Foto do Produto', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Anunciar')


class RatingForm(FlaskForm):
    stars = RadioField('Avaliação', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], validators=[InputRequired()])
    comment = TextAreaField('Comentário')
    submit = SubmitField('Avaliar')
