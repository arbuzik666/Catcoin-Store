from flask import Blueprint

favorites_bp = Blueprint('favorites', __name__, template_folder='templates/favorites')

from . import routes