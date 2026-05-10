from flask import render_template, abort, request, flash, redirect, url_for
from flask_login import current_user, login_required
from models import Product, Review, Order, OrderItem, Category, db
from . import main_bp

@main_bp.route('/')
@main_bp.route('/category/<int:category_id>')
def index(category_id=None):
    """Главная страница магазина с фильтром по категориям и поиском"""
    
    categories = Category.query.order_by(Category.name).all()
    
    search_query = request.args.get('q', '').strip()
    
    query = Product.query
    
    if category_id:
        category = Category.query.get_or_404(category_id)
        query = query.filter(Product.categories.contains(category))
    
    if search_query:
        search_query = search_query.lower()
        query = query.filter(
            db.func.lower(Product.name).contains(search_query)
        )
    


    products = query.order_by(Product.created_at.desc()).all()
    
    return render_template('main/index.html', 
                         products=products, 
                         categories=categories,
                         current_category_id=category_id,
                         search_query=search_query)


@main_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    """Страница товара с отзывами"""
    product = Product.query.get(product_id)
    
    if product is None:
        abort(404)
    
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('🐱 Войдите, чтобы оставить отзыв!', 'error')
            return redirect(url_for('auth.login', next=request.url))
        
        has_purchased = db.session.query(OrderItem).join(Order).filter(
            Order.user_id == current_user.id,
            OrderItem.product_id == product_id,
            Order.status != 'отменён'
        ).first()
        
        if not has_purchased:
            flash('🐱 Вы можете оставить отзыв только после покупки этого товара!', 'error')
            return redirect(url_for('main.product_detail', product_id=product_id))
        
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        
        if not rating:
            flash('🐱 Поставьте оценку!', 'error')
            return redirect(url_for('main.product_detail', product_id=product_id))
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            flash('🐱 Оценка должна быть от 1 до 5!', 'error')
            return redirect(url_for('main.product_detail', product_id=product_id))
        
        existing_review = Review.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id
        ).first()
        
        if existing_review:
            flash('🐱 Вы уже оставили отзыв на этот товар!', 'info')
            return redirect(url_for('main.product_detail', product_id=product_id))
        
        review = Review(
            user_id=current_user.id,
            product_id=product_id,
            rating=rating,
            comment=comment or ''
        )
        db.session.add(review)
        db.session.commit()
        
        flash('🐾 Спасибо за отзыв!', 'success')
        return redirect(url_for('main.product_detail', product_id=product_id))
    
    reviews = Review.query.filter_by(product_id=product_id)\
                         .order_by(Review.created_at.desc())\
                         .all()
    
    return render_template('main/product.html', product=product, reviews=reviews)

@main_bp.route('/about')
def about():
    """Страница «О нас»"""
    return render_template('main/about.html')


@main_bp.route('/review/edit/<int:review_id>', methods=['POST'])
@login_required
def edit_review(review_id):
    """Редактирование отзыва"""
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != current_user.id:
        flash('🐱 Вы не можете редактировать чужой отзыв!', 'error')
        return redirect(url_for('main.product_detail', product_id=review.product_id))
    
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    
    if not rating:
        flash('🐱 Поставьте оценку!', 'error')
        return redirect(url_for('main.product_detail', product_id=review.product_id))
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError
    except ValueError:
        flash('🐱 Оценка должна быть от 1 до 5!', 'error')
        return redirect(url_for('main.product_detail', product_id=review.product_id))
    
    review.rating = rating
    review.comment = comment or ''
    db.session.commit()
    
    flash('🐾 Отзыв обновлён!', 'success')
    return redirect(url_for('main.product_detail', product_id=review.product_id))


@main_bp.route('/review/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    """Удаление отзыва"""
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != current_user.id and not current_user.is_admin:
        flash('🐱 Вы не можете удалить чужой отзыв!', 'error')
        return redirect(url_for('main.product_detail', product_id=review.product_id))
    
    product_id = review.product_id
    db.session.delete(review)
    db.session.commit()
    
    flash('🐾 Отзыв удалён!', 'info')
    return redirect(url_for('main.product_detail', product_id=product_id))