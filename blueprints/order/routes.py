from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Order, OrderItem, CartItem
from . import order_bp


@order_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Оформление заказа"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('🐱 Корзина пуста! Добавьте товары.', 'info')
        return redirect(url_for('cart.view_cart'))
    
    total = sum(item.total_price for item in cart_items)
    
    if request.method == 'POST':
        order = Order(
            user_id=current_user.id,
            total_price=total,
            status='новый'
        )
        db.session.add(order)
        db.session.flush() 
        
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price  
            )
            db.session.add(order_item)
            
            product = cart_item.product
            product.stock -= cart_item.quantity
        
        for cart_item in cart_items:
            db.session.delete(cart_item)
        
        db.session.commit()
        
        flash('🐾 Заказ успешно оформлен! Спасибо за покупку!', 'success')
        return redirect(url_for('order.order_confirmation', order_id=order.id))
    
    return render_template('order/checkout.html', 
                         cart_items=cart_items, 
                         total=total)


@order_bp.route('/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    """Страница подтверждения заказа"""
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        flash('🐱 Это не ваш заказ!', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('order/confirmation.html', order=order)


@order_bp.route('/my-orders')
@login_required
def my_orders():
    """История заказов пользователя"""
    orders = Order.query.filter_by(user_id=current_user.id)\
                       .order_by(Order.created_at.desc())\
                       .all()
    
    return render_template('order/my_orders.html', orders=orders)