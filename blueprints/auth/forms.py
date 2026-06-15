from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


class LoginForm(FlaskForm):
    """Форма входа"""
    email = StringField('Email', validators=[
        DataRequired(message='🐱 Email обязателен!'),
        Email(message='🐱 Введите настоящий email!')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='🐱 Пароль обязателен!')
    ])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('🐾 Войти')


class RegistrationForm(FlaskForm):
    """Форма регистрации"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='🐱 Имя обязательно!'),
        Length(min=2, max=64, message='🐱 Имя должно быть от 2 до 64 символов!')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='🐱 Email обязателен!'),
        Email(message='🐱 Введите настоящий email!')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='🐱 Пароль обязателен!'),
        Length(min=6, message='🐱 Пароль должен быть минимум 6 символов!')
    ])
    password2 = PasswordField('Повторите пароль', validators=[
        DataRequired(message='🐱 Повторите пароль!'),
        EqualTo('password', message='🐱 Пароли не совпадают!')
    ])
    submit = SubmitField('🐾 Зарегистрироваться')