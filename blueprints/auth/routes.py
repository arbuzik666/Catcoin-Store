from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from . import auth_bp
from .forms import LoginForm, RegistrationForm


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('🐱 Пользователь с таким именем уже существует!', 'error')
            return render_template('auth/register.html', form=form)
        
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('🐱 Этот email уже зарегистрирован!', 'error')
            return render_template('auth/register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('🐾 Регистрация успешна! Теперь можно войти.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в аккаунт"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('🐱 Неверный email или пароль!', 'error')
            return render_template('auth/login.html', form=form)
        
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        flash(f'🐾 С возвращением, {user.username}!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Выход из аккаунта"""
    logout_user()
    flash('🐾 Вы вышли из аккаунта. Заходите ещё!', 'info')
    return redirect(url_for('main.index'))