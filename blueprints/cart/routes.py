from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Product, CartItem
from . import cart_bp


@cart_bp.route('/cart')
@login_required
def view_cart():
    """Просмотр корзины"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    total = sum(item.total_price for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    
    return render_template('cart/view_cart.html', 
                         cart_items=cart_items, 
                         total=total,
                         total_items=total_items)


@cart_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Добавление товара в корзину"""
    product = Product.query.get_or_404(product_id)
    
    if not product.in_stock:
        flash('🐱 К сожалению, этот товар закончился!', 'error')
        return redirect(url_for('main.product_detail', product_id=product_id))
    
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id, 
        product_id=product_id
    ).first()
    
    if cart_item:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            flash(f'🐾 Количество "{product.name}" в корзине увеличено!', 'success')
        else:
            flash(f'🐱 Больше нет в наличии!', 'error')
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=1
        )
        db.session.add(cart_item)
        flash(f'🐾 "{product.name}" добавлен в корзину!', 'success')
    
    db.session.commit()
    
    referrer = request.referrer
    if referrer and 'product' in referrer:
        return redirect(referrer)
    
    return redirect(url_for('main.index'))


@cart_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    """Обновление количества товара в корзине"""
    cart_item = CartItem.query.get_or_404(item_id)
    
    if cart_item.user_id != current_user.id:
        flash('🐱 Нельзя трогать чужую корзину!', 'error')
        return redirect(url_for('cart.view_cart'))
    
    try:
        new_quantity = int(request.form.get('quantity', 1))
    except ValueError:
        new_quantity = 1
    
    if new_quantity <= 0:
        db.session.delete(cart_item)
        flash('🐾 Товар удалён из корзины', 'info')
    elif new_quantity > cart_item.product.stock:
        cart_item.quantity = cart_item.product.stock
        flash(f'🐱 Максимальное количество — {cart_item.product.stock} шт.', 'error')
    else:
        cart_item.quantity = new_quantity
    
    db.session.commit()
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Удаление товара из корзины"""
    cart_item = CartItem.query.get_or_404(item_id)
    
    if cart_item.user_id != current_user.id:
        flash('🐱 Нельзя трогать чужую корзину!', 'error')
        return redirect(url_for('cart.view_cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('🐾 Товар удалён из корзины', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/count')
@login_required
def cart_count():
    """API: количество товаров в корзине (для навигации)"""
    total = sum(item.quantity for item in current_user.cart_items)
    return jsonify({'count': total})

@cart_bp.app_context_processor
def inject_cart_count():
    """Добавляет количество товаров в корзине во все шаблоны"""
    from flask_login import current_user
    if current_user.is_authenticated:
        count = sum(item.quantity for item in current_user.cart_items)
    else:
        count = 0
    return {'cart_count': count}