from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Product, Favorite
from . import favorites_bp


@favorites_bp.route('/favorites')
@login_required
def view_favorites():
    """Просмотр избранного"""
    favorites = Favorite.query.filter_by(user_id=current_user.id)\
                             .order_by(Favorite.created_at.desc())\
                             .all()
    
    products = [fav.product for fav in favorites]
    
    return render_template('favorites/view.html', products=products)


@favorites_bp.route('/favorites/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_favorite(product_id):
    """Добавление/удаление из избранного"""
    product = Product.query.get_or_404(product_id)
    
    existing = Favorite.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'removed', 'message': f'🐾 "{product.name}" удалён из избранного!'})
        
        flash(f'🐾 "{product.name}" удалён из избранного!', 'info')
    else:
        favorite = Favorite(user_id=current_user.id, product_id=product_id)
        db.session.add(favorite)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'added', 'message': f'🐾 "{product.name}" добавлен в избранное! ❤️'})
        
        flash(f'🐾 "{product.name}" добавлен в избранное! ❤️', 'success')
    
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for('main.index'))


@favorites_bp.route('/favorites/check/<int:product_id>')
@login_required
def check_favorite(product_id):
    """Проверка, в избранном ли товар (для иконки сердечка)"""
    existing = Favorite.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    return jsonify({'is_favorite': existing is not None})


@favorites_bp.app_context_processor
def inject_favorites_count():
    """Добавляет количество избранного во все шаблоны"""
    from flask_login import current_user
    if current_user.is_authenticated:
        count = Favorite.query.filter_by(user_id=current_user.id).count()
    else:
        count = 0
    return {'favorites_count': count}

@favorites_bp.route('/favorites/count')
@login_required
def favorites_count_api():
    """API: количество избранного"""
    count = Favorite.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})