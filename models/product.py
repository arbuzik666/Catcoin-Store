from datetime import datetime
from . import db

product_category = db.Table('product_category',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    
    products = db.relationship('Product', secondary=product_category,
                               backref=db.backref('categories', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_file = db.Column(db.String(128), default='default_product.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    cart_items = db.relationship('CartItem', backref='product', lazy='dynamic')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    
    def get_image_url(self):
        return f'/static/images/{self.image_file}'
    
    @property
    def in_stock(self):
        return self.stock > 0
    
    @property
    def avg_rating(self):
        if not self.reviews:
            return 0
        total = sum(review.rating for review in self.reviews)
        return round(total / len(self.reviews), 1)
    
    @property
    def reviews_count(self):
        """Количество отзывов"""
        return len(self.reviews)
    
    def __repr__(self):
        return f'<Product {self.name} - {self.price} ₽>'