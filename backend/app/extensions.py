from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_migrate import Migrate # type: ignore
from flask_jwt_extended import JWTManager # type: ignore
from flask import jsonify

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# 詳細的 JWT 錯誤處理程序
@jwt.invalid_token_loader
def invalid_token_callback(error_message):
    """無效令牌的處理"""
    print(f"無效令牌錯誤: {error_message}")
    return jsonify({
        'status': 'error',
        'message': f'無效的認證令牌: {error_message}',
        'code': 'invalid_token'
    }), 422

@jwt.unauthorized_loader
def missing_token_callback(error_message):
    """缺少令牌的處理"""
    print(f"缺少令牌錯誤: {error_message}")
    return jsonify({
        'status': 'error',
        'message': f'請求缺少認證令牌: {error_message}',
        'code': 'authorization_required'
    }), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    """過期令牌的處理"""
    print(f"令牌已過期: {jwt_header}, {jwt_data}")
    return jsonify({
        'status': 'error',
        'message': '認證令牌已過期',
        'code': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_format_callback(error):
    return jsonify({
        "message": "令牌格式不正確",
        "error": error
    }), 422