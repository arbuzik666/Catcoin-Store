import os
from flask import Flask
from config import Config
from models import db, login_manager
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    
    login_manager.init_app(app)
    
    from blueprints.main import main_bp
    app.register_blueprint(main_bp)
    
    from blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from blueprints.cart import cart_bp
    app.register_blueprint(cart_bp, url_prefix='/cart')
    
    from blueprints.order import order_bp
    app.register_blueprint(order_bp, url_prefix='/order')
    
    from blueprints.admin import admin_bp
    app.register_blueprint(admin_bp)

    from blueprints.favorites import favorites_bp
    app.register_blueprint(favorites_bp, url_prefix='/favorites')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    return app


def init_db():
    from models import Category, User
    
    db.create_all()
    print("✅ База данных готова (SQLite)")
    
    categories_list = [
        {'name': 'Дом и уют', 'description': 'Товары для дома с кошачьим дизайном'},
        {'name': 'Аксессуары', 'description': 'Стильные аксессуары с котиками'},
        {'name': 'Одежда', 'description': 'Одежда и обувь с кошачьими принтами'},
        {'name': 'Красота', 'description': 'Косметика и уход с котиками'},
        {'name': 'Канцелярия', 'description': 'Тетради, ручки и стикеры с котами'},
        {'name': 'Гаджеты', 'description': 'Электроника с кошачьим дизайном'},
        {'name': 'Подарки', 'description': 'Идеи подарков для любителей котиков'},
        {'name': 'Для кухни', 'description': 'Посуда и кухонные принадлежности'},
        {'name': 'Сладости', 'description': 'Вкусняшки в кошачьем стиле'},
        {'name': 'Книги', 'description': 'Книги и комиксы про котиков'},
        {'name': 'Игрушки', 'description': 'Игрушки с котами'},
        {'name': 'Спорт', 'description': 'Спортивные товары с кошачьими принтами'},
    ]
    
    added = 0
    for cat_data in categories_list:
        existing = Category.query.filter_by(name=cat_data['name']).first()
        if not existing:
            category = Category(**cat_data)
            db.session.add(category)
            added += 1
    
    if added > 0:
        print(f"✅ Добавлено {added} новых категорий")
    else:
        print("📋 Категории уже существуют")
    
    admin = User.query.filter_by(email='admin@email.com').first()
    
    if not admin:
        admin = User(
            username='admin',
            email='admin@email.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("✅ Создан администратор:")
        print("   📧 Email: admin@email.com")
        print("   🔑 Пароль: admin123")
    else:
        if not admin.is_admin:
            admin.is_admin = True
            print("✅ Права администратора выданы существующему пользователю")
        else:
            print("👑 Администратор уже существует")
    
    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        init_db()
    
    print("🚀 Запуск сервера")
    app.run(debug=True, port=5000)