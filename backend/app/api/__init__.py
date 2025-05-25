from flask import Blueprint

api_bp = Blueprint('api', __name__)
comments_bp = Blueprint('comments', __name__)

# 導入路由模組
from . import auth, chat, comments, users, accommodations, reviews, maintenance, sublets, admin, verification, stats

# 註冊錯誤處理器
@api_bp.errorhandler(404)
def not_found(error):
    return {'error': 'Not Found'}, 404

@api_bp.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal Server Error'}, 500