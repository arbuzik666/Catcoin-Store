from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '🐱 Пожалуйста, войдите, чтобы получить доступ.'
login_manager.login_message_category = 'info'

from .user import User
from .product import Product, Category
from .order import CartItem, Order, OrderItem
from .review import Review 
from .favorite import Favorite  