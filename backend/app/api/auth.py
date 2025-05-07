import requests # type: ignore
import os
import base64
import json

from flask import request, jsonify, current_app
from flask_jwt_extended import ( # type: ignore
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity
) 
from datetime import datetime, timedelta
from app.api import api_bp
from app.models.user import User, StudentVerification
from app.extensions import db


# 從環境變數或配置文件獲取
CLIENT_ID = os.environ.get('NCU_OAUTH_CLIENT_ID')
CLIENT_SECRET = os.environ.get('NCU_OAUTH_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('NCU_OAUTH_REDIRECT_URI')

@api_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 檢查必要欄位
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'message': '缺少必要欄位'}), 400
    
    # 檢查電子郵件是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': '此電子郵件已被註冊'}), 400
    
    # 建立新用戶
    user = User(
        username=data['username'],
        email=data['email'],
        user_role=data.get('user_role', 'student')
    )
    user.set_password(data['password'])
    
    # 其他可選欄位
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'phone' in data:
        user.phone = data['phone']
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': '註冊成功',
        'user_id': user.user_id
    }), 201

@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'message': '缺少必要欄位'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': '電子郵件或密碼錯誤'}), 401
    
    if not user.is_active:
        return jsonify({'message': '帳號已被停用'}), 403
    
    # 更新最後登入時間
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # 生成 JWT token
    access_token = create_access_token(identity=user.user_id)
    refresh_token = create_refresh_token(identity=user.user_id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.user_id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.user_role,
            'is_verified': user.is_verified
        }
    }), 200

@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    
    return jsonify({'access_token': access_token}), 200

@api_bp.route('/auth/portal-callback', methods=['POST'])
def portal_callback():
    data = request.json
    
    if not data or not data.get('code'):
        return jsonify({"message": "缺少授權碼"}), 400
    
    code = data.get('code')
    
    try:
        # 1. 向 Portal 系統交換 token
        token_url = 'https://portal.ncu.edu.tw/oauth2/token'
        auth_header = base64.b64encode(f"{os.environ.get('NCU_OAUTH_CLIENT_ID')}:{os.environ.get('NCU_OAUTH_CLIENT_SECRET', '')}".encode()).decode()
        
        token_response = requests.post(
            token_url,
            headers={
                'Authorization': f'Basic {auth_header}',
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI
            }
        )
        
        token_data = token_response.json()
        
        if 'access_token' not in token_data:
            return jsonify({"message": "無法獲取訪問令牌"}), 401
        
        # 2. 獲取用戶資訊
        user_info_url = 'https://portal.ncu.edu.tw/apis/oauth/v1/info'
        user_response = requests.get(
            user_info_url,
            headers={
                'Authorization': f'Bearer {token_data["access_token"]}'
            }
        )
        
        user_info = user_response.json()
        
        # 3. 處理用戶資訊，查找或創建用戶
        identifier = user_info.get('identifier')
        if not identifier:
            return jsonify({"message": "無法獲取用戶識別碼"}), 400
        
        # 查找是否有現有用戶
        user = User.query.filter_by(portal_id=identifier).first()
        
        # 如果沒有，創建新用戶
        if not user:
            user = User(
                username=user_info.get('chineseName', identifier),
                email=user_info.get('email', f"{identifier}@cc.ncu.edu.tw"),
                portal_id=identifier,
                first_name=user_info.get('chineseName', '').split(' ')[0] if user_info.get('chineseName') else '',
                last_name=' '.join(user_info.get('chineseName', '').split(' ')[1:]) if user_info.get('chineseName') else '',
                phone=user_info.get('mobilePhone', ''),
                is_verified=True,  # 從 Portal 登入的用戶自動驗證
                user_role='student'  # 默認為學生角色
            )
            
            # 生成隨機密碼
            import secrets
            random_password = secrets.token_urlsafe(16)
            user.set_password(random_password)
            
            db.session.add(user)
            db.session.commit()
            
            # 如果有學生身份資訊，創建學生驗證記錄
            if 'academyRecords' in user_info and user_info.get('studentId'):
                student_verification = StudentVerification(
                    user_id=user.user_id,
                    student_id=user_info.get('studentId', ''),
                    department=user_info.get('academyRecords', {}).get('didGroup', ''),
                    verified_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(days=365),  # 一年有效期
                    verification_status='verified'
                )
                db.session.add(student_verification)
                db.session.commit()
        
        # 更新最後登入時間
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 4. 生成 JWT 令牌
        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)

        # 獲取學生ID（如果有）
        student_verification = StudentVerification.query.filter_by(user_id=user.user_id).first()
        student_id = student_verification.student_id if student_verification else None
        
        # 返回令牌和用戶信息
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.user_id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.user_role,
                "is_verified": user.is_verified,
                "student_id": student_id
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Portal 登入錯誤: {str(e)}")
        return jsonify({"message": f"登入過程中發生錯誤: {str(e)}"}), 500