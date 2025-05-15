import requests # type: ignore
import os
import base64
import json
import traceback
import uuid
from flask import session # type: ignore
from flask import request, jsonify, current_app
from datetime import datetime, timedelta

from app.api import api_bp
from app.models.user import User, PasswordReset
from app.utils.email import send_email
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
        
@api_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """處理忘記密碼請求，發送重設密碼郵件"""
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': '請提供電子郵件'}), 400
        
        # 檢查使用者是否存在
        user = User.query.filter_by(email=email).first()
        if not user:
            # 出於安全考慮，不透露用戶是否存在
            return jsonify({'success': True, 'message': '如果此電子郵件有關聯帳戶，您將收到重設密碼的郵件'}), 200
        
        # 檢查是否已經有活動的重設令牌，如果有則刪除
        existing_tokens = PasswordReset.query.filter_by(user_id=user.user_id).all()
        for token in existing_tokens:
            db.session.delete(token)
        
        # 生成唯一的重設令牌
        reset_token = str(uuid.uuid4())
        token_expiry = datetime.utcnow() + timedelta(hours=24)
        
        # 保存令牌到資料庫
        password_reset = PasswordReset(
            user_id=user.user_id,
            token=reset_token,
            expiry=token_expiry
        )
        db.session.add(password_reset)
        db.session.commit()
        
        # 生成重設鏈接 - 使用前端部署的URL (假設從環境變數取得)
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:8080')
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        # 準備郵件內容
        email_subject = "中央大學校外外宿網 - 密碼重設請求"
        email_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #4a90e2;">中央大學校外外宿網</h2>
            </div>
            
            <p>親愛的 {user.username}：</p>
            
            <p>我們收到了重設您密碼的請求。如果這是您操作的，請點擊下方按鈕重設密碼：</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" style="background-color: #4a90e2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">重設我的密碼</a>
            </div>
            
            <p>或者，您可以複製以下連結到瀏覽器地址欄：</p>
            <p style="background-color: #f5f5f5; padding: 10px; word-break: break-all;">{reset_link}</p>
            
            <p>此連結將在 <strong>24 小時後失效</strong>。如果您沒有請求重設密碼，請忽略此郵件，您的帳戶仍然安全。</p>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px;">
                <p>此郵件由系統自動發送，請勿回覆。</p>
                <p>&copy; 2025 中央大學校外外宿網</p>
            </div>
        </div>
        """
        
        # 發送郵件
        send_email(user.email, email_subject, email_body)
        
        return jsonify({
            'success': True, 
            'message': '如果此電子郵件有關聯帳戶，您將收到重設密碼的郵件'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"忘記密碼處理錯誤: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False, 
            'message': f'處理請求時發生錯誤: {str(e)}'
        }), 500

@api_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """驗證令牌並重設密碼"""
    try:
        data = request.json
        token = data.get('token')
        password = data.get('password')
        
        if not token or not password:
            return jsonify({
                'success': False, 
                'message': '請提供重設令牌和新密碼'
            }), 400
        
        # 檢查令牌是否存在且有效
        reset_record = PasswordReset.query.filter_by(token=token).first()
        
        if not reset_record:
            return jsonify({
                'success': False, 
                'message': '無效的重設連結，可能已經使用過或不存在'
            }), 400
        
        # 檢查令牌是否過期
        if reset_record.expiry < datetime.utcnow():
            db.session.delete(reset_record)
            db.session.commit()
            return jsonify({
                'success': False, 
                'message': '重設連結已過期，請重新申請重設密碼'
            }), 400
        
        # 獲取使用者並更新密碼
        user = User.query.get(reset_record.user_id)
        
        if not user:
            return jsonify({
                'success': False, 
                'message': '無法找到相關帳戶'
            }), 400
        
        # 更新密碼
        user.set_password(password)
        
        # 刪除使用過的重設令牌
        db.session.delete(reset_record)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '密碼已成功重設，請使用新密碼登入'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"重設密碼錯誤: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False, 
            'message': f'重設密碼過程中發生錯誤: {str(e)}'
        }), 500