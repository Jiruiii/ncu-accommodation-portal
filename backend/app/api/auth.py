import requests # type: ignore
import os
import base64
import json
import traceback

from flask import session # type: ignore
from flask import request, jsonify, current_app
# from flask_jwt_extended import ( # type: ignore
#     create_access_token, create_refresh_token, 
#     jwt_required, get_jwt_identity
# ) 

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
        user_role=data.get('user_role', 'student'),
        phone = data['phone']
    )
    user.set_password(data['password'])
    
    if 'portal_id' in data:
        user.portal_id = data['portal_id']
        user.is_verified = True
    
    if 'school_email' in data:
        user.school_email = data['school_email']
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': '註冊成功',
        'user_id': user.user_id
    }), 200

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
    
    # session 設置
    session.clear()
    session['user_id'] = user.user_id
    session['username'] = user.username
    session['user_role'] = user.user_role
    session.permanent = True
    
    return jsonify({
        'message': '登入成功',
        'user': {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "profile_image": user.profile_image,
            "user_role": user.user_role,
            "has_protal_id": bool(user.portal_id), 
            'is_admin': user.is_admin(),
            'is_superuser': user.is_superuser(),
        }
    }), 200
    
@api_bp.route('/auth/status', methods=['GET'])
def check_auth_status():
    """檢查當前用戶的認證狀態"""
    try:
        if 'user_id' not in session:
            return jsonify({
                "authenticated": False,
                "message": "未登入"
            })
        
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            # 用戶不存在，清除 session
            session.clear()
            return jsonify({
                "authenticated": False,
                "message": "用戶不存在"
            })
        
        # 返回當前用戶信息
        return jsonify({
            "authenticated": True,
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "user_role": user.user_role,
                "is_admin": user.is_admin(),
                "is_superuser": user.is_superuser()
            },
            "session_data": dict(session)  # 調試用
        })
    except Exception as e:
        print(f"檢查認證狀態時出錯: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "authenticated": False,
            "error": str(e)
        }), 500

@api_bp.route('/auth/portal-callback', methods=['POST'])
def portal_callback():
    data = request.json
    
    if not data or not data.get('code'):
        return jsonify({"success": False, "message": "缺少授權碼"}), 400
    
    code = data.get('code')
    # 修正參數名稱從 actiontype 改為 action_type
    action_type = data.get('action_type', 'login')
    
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
            return jsonify({"success": False, "message": "無法獲取訪問令牌"}), 401
        
        # 2. 獲取用戶資訊
        user_info_url = 'https://portal.ncu.edu.tw/apis/oauth/v1/info'
        user_response = requests.get(
            user_info_url,
            headers={
                'Authorization': f'Bearer {token_data["access_token"]}'
            }
        )
        
        user_info = user_response.json()
        
        # 3. 處理用戶資訊
        identifier = user_info.get('identifier')
        if not identifier:
            return jsonify({"success": False, "message": "無法獲取用戶識別碼"}), 400
        
        # 4. 根據操作類型處理不同的邏輯
        if action_type == 'login':
            # 快速登入邏輯：檢查是否存在此 Portal ID 的用戶
            user = User.query.filter_by(portal_id=identifier).first()
            
            if not user:
                # 找不到對應的用戶，返回錯誤信息
                return jsonify({
                    "success": False,
                    "message": "此 Portal 帳號尚未綁定，請先使用電子郵件登入後在個人資料頁面綁定"
                }), 404
            
            # 找到用戶，執行登入
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['user_role'] = user.user_role
            session.permanent = True
            
            # 更新最後登入時間
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # 返回用戶資訊
            return jsonify({
                "success": True,
                "message": "Portal 快速登入成功",
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "profile_image": user.profile_image,
                    "user_role": user.user_role,
                    "has_portal_id": True,
                    "school_email": user.school_email,
                    'is_admin': user.is_admin(),
                    'is_superuser': user.is_superuser(),
                }
            })
            
        elif action_type == 'binding':
            # 處理已登入用戶的綁定操作
            
            # 檢查此 Portal ID 是否已被綁定
            existing_user = User.query.filter_by(portal_id=identifier).first()
            if existing_user:
                # 此 Portal ID 已被綁定
                if 'user_id' in session and existing_user.user_id == session.get('user_id'):
                    # 已經綁定到當前登入用戶
                    return jsonify({
                        "success": False,
                        "message": "您已綁定此 Portal 帳號"
                    }), 400
                else:
                    # 綁定到其他用戶
                    return jsonify({
                        "success": False,
                        "message": "此 Portal 帳號已被其他用戶綁定"
                    }), 400
            
            # 確認用戶已登入
            if 'user_id' not in session:
                return jsonify({
                    "success": False,
                    "message": "您需要先登入才能綁定 Portal 帳號"
                }), 401
                
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({
                    "success": False,
                    "message": "找不到您的用戶資訊"
                }), 404
            
            # 綁定 Portal ID
            user.portal_id = identifier
            user.school_email = user_info.get('email', f"{identifier}@cc.ncu.edu.tw")
            user.is_verified = True
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Portal 綁定成功",
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "portal_id": user.portal_id,
                    "school_email": user.school_email
                }
            })
        
        # 專門用於註冊前獲取資訊的操作類型
        elif action_type == 'getinfo':
            # 檢查此 Portal ID 是否已被使用
            existing_user = User.query.filter_by(portal_id=identifier).first()
            if existing_user:
                return jsonify({
                    "success": False,
                    "message": "此 Portal 帳號已被其他用戶綁定，無法在註冊時使用"
                }), 400
            
            # 獲取需要的 Portal 資訊
            student_id = identifier
            name = user_info.get('chineseName', '')
            school_email = user_info.get('email', f"{identifier}@cc.ncu.edu.tw")
            
            return jsonify({
                "success": True,
                "message": "獲取 Portal 資訊成功",
                "portal_data": {
                    "student_id": student_id,
                    "name": name,
                    "school_email": school_email,
                }
            })
        
        else:
            # 未知的操作類型
            return jsonify({
                "success": False,
                "message": f"無效的操作類型: {action_type}"
            }), 400
            
    except Exception as e:
        print(f"Portal 回調處理錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": f"處理失敗: {str(e)}"
        }), 500
    
@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    """登出用戶，清除 session"""
    try:
        # 清除 session 數據
        session.clear()
        return jsonify({
            "success": True,
            "message": "成功登出"
        }), 200
    except Exception as e:
        current_app.logger.error(f"登出錯誤: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"登出過程中發生錯誤: {str(e)}"
        }), 500