import os
import uuid
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Product, Category, Order, User
from . import admin_bp

def admin_required(func):
    from functools import wraps
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            flash('🐱 Доступ только для администраторов!', 'error')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return wrapper

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Проверяет, разрешён ли формат файла"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file):
    """Сохраняет картинку и возвращает имя файла"""
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return filename
    return None

@admin_bp.route('/admin')
@admin_required
def dashboard():
    """Главная страница админ-панели"""
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    low_stock = Product.query.filter(Product.stock < 5).all()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         total_orders=total_orders,
                         total_users=total_users,
                         recent_orders=recent_orders,
                         low_stock=low_stock)

@admin_bp.route('/admin/products')
@admin_required
def admin_products():
    """Список всех товаров"""
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)


@admin_bp.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    """Добавление нового товара"""
    categories = Category.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').lower().strip()
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        category_ids = request.form.getlist('categories')
        
        if not name or not price:
            flash('🐱 Название и цена обязательны!', 'error')
            return render_template('admin/add_product.html', categories=categories)
        
        try:
            price = float(price)
            stock = int(stock) if stock else 0
        except ValueError:
            flash('🐱 Некорректная цена или количество!', 'error')
            return render_template('admin/add_product.html', categories=categories)

        if price < 0:
            flash('🐱 Цена не может быть отрицательной!', 'error')
            return render_template('admin/add_product.html', categories=categories)

        if price > 99999999:
            flash('🐱 Цена слишком большая (максимум 99 999 999 ₽)!', 'error')
            return render_template('admin/add_product.html', categories=categories)

        if stock < 0:
            flash('🐱 Количество не может быть отрицательным!', 'error')
            return render_template('admin/add_product.html', categories=categories)

        if stock > 999999:
            flash('🐱 Количество слишком большое (максимум 999 999 шт.)!', 'error')
            return render_template('admin/add_product.html', categories=categories)
        
        image_file = 'default_product.png'  
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                saved_filename = save_image(file)
                if saved_filename:
                    image_file = saved_filename
                else:
                    flash('🐱 Неподдерживаемый формат файла! Используй PNG, JPG, GIF или WEBP.', 'error')
                    return render_template('admin/add_product.html', categories=categories)
        
        product = Product(
            name=name,
            description=description or '',
            price=price,
            stock=stock,
            image_file=image_file
        )
        
        if category_ids:
            cats = Category.query.filter(Category.id.in_(category_ids)).all()
            product.categories = cats
        
        db.session.add(product)
        db.session.commit()
        
        flash(f'🐾 Товар "{product.name}" добавлен!', 'success')
        return redirect(url_for('admin.admin_products'))
    
    return render_template('admin/add_product.html', categories=categories)


@admin_bp.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    """Редактирование товара"""
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        product.name = request.form.get('name', product.name).lower().strip()
        product.description = request.form.get('description', product.description)
        
        try:
            new_price = float(request.form.get('price', product.price))
            new_stock = int(request.form.get('stock', product.stock))
        except ValueError:
            flash('🐱 Некорректная цена или количество!', 'error')
            return render_template('admin/edit_product.html', product=product, categories=categories)

        if new_price < 0:
            flash('🐱 Цена не может быть отрицательной!', 'error')
            return render_template('admin/edit_product.html', product=product, categories=categories)

        if new_price > 99999999:
            flash('🐱 Цена слишком большая (максимум 99 999 999 ₽)!', 'error')
            return render_template('admin/edit_product.html', product=product, categories=categories)

        if new_stock < 0:
            flash('🐱 Количество не может быть отрицательным!', 'error')
            return render_template('admin/edit_product.html', product=product, categories=categories)

        if new_stock > 999999:
            flash('🐱 Количество слишком большое (максимум 999 999 шт.)!', 'error')
            return render_template('admin/edit_product.html', product=product, categories=categories)

        product.price = new_price
        product.stock = new_stock
        
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                saved_filename = save_image(file)
                if saved_filename:
                    if product.image_file != 'default_product.png':
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_file)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    
                    product.image_file = saved_filename
                else:
                    flash('🐱 Неподдерживаемый формат файла!', 'error')
                    return render_template('admin/edit_product.html', product=product, categories=categories)
        
        category_ids = request.form.getlist('categories')
        if category_ids:
            product.categories = Category.query.filter(Category.id.in_(category_ids)).all()
        else:
            product.categories = []
        
        db.session.commit()
        flash(f'🐾 Товар "{product.name}" обновлён!', 'success')
        return redirect(url_for('admin.admin_products'))
    
    return render_template('admin/edit_product.html', product=product, categories=categories)


@admin_bp.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    """Удаление товара"""
    product = Product.query.get_or_404(product_id)
    
    if product.image_file != 'default_product.png':
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_file)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'🐾 Товар "{name}" удалён!', 'info')
    return redirect(url_for('admin.admin_products'))

@admin_bp.route('/admin/orders')
@admin_required
def admin_orders():
    """Все заказы"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)


@admin_bp.route('/admin/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    """Детали заказа"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/admin/orders/status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Обновление статуса заказа"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['новый', 'обработан', 'отправлен', 'доставлен', 'отменён']:
        order.status = new_status
        db.session.commit()
        flash(f'🐾 Статус заказа №{order.id} изменён на "{new_status}"!', 'success')
    
    return redirect(url_for('admin.order_detail', order_id=order_id))


@admin_bp.route('/admin/users')
@admin_required
def admin_users():
    """Список пользователей"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)