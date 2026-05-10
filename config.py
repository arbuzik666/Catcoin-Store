import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'catcoin-secret-key-change-me'
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'catcoin.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SHOP_NAME = 'Catcoin Store'
    PRODUCTS_PER_PAGE = 12
    WTF_CSRF_ENABLED = True
    
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 