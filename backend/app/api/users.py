from flask import request, jsonify, current_app, session
from app.api import api_bp
from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime
import os
from werkzeug.utils import secure_filename
import uuid
import traceback

# 用戶身份驗證裝飾器
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "請先登入"}), 401
        
        return f(*args, **kwargs)
    return decorated

# 檢查是否為本人或管理員
def check_owner(user_id):
    if 'user_id' not in session:
        return False
    
    current_user_id = session.get('user_id')
    current_user = User.query.get(current_user_id)
    
    # 檢查是否為本人或管理員
    return str(current_user_id) == str(user_id) or (current_user and current_user.is_admin())

# 獲取當前用戶個人資料
@api_bp.route('/users/profile', methods=['GET'])
@login_required
def get_profile():
    try:
        user_id = session.get('user_id')
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "school_email": user.school_email,
                "phone": user.phone,
                "profile_image": user.profile_image,
                "user_role": user.user_role,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "has_portal_id": bool(user.portal_id), 
            }
        })
    except Exception as e:
        print(f"獲取用戶資料錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"message": f"獲取用戶資料失敗: {str(e)}"}), 500

# 更新用戶個人資料
@api_bp.route('/users/profile', methods=['PUT'])
@login_required
def update_profile():
    try:
        user_id = session.get('user_id')
        user = User.query.get_or_404(user_id)
        
        # 獲取請求的 JSON 資料
        data = request.get_json()
        
        # 只允許更新特定欄位
        allowed_fields = ['phone', 'bio','username', 'email']
        
        # 更新用戶資料
        for field in allowed_fields:
            if field in data:
                # 檢查電子郵件唯一性
                if field == 'email' and data['email'] != user.email:
                    existing_user = User.query.filter_by(email=data['email']).first()
                    if existing_user:
                        return jsonify({"message": "此電子郵件已被使用"}), 400
                
                # 檢查用戶名唯一性
                if field == 'username' and data['username'] != user.username:
                    existing_user = User.query.filter_by(username=data['username']).first()
                    if existing_user:
                        return jsonify({"message": "此用戶名已被使用"}), 400
                
                setattr(user, field, data[field])
        
        user.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "個人資料已更新",
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "profile_image": user.profile_image,
                "bio": user.bio,
                "user_role": user.user_role,
                "is_verified": user.is_verified
            }
        })
    except Exception as e:
        db.session.rollback()
        print(f"更新用戶資料錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"message": f"更新用戶資料失敗: {str(e)}"}), 500

# 上傳個人頭像
@api_bp.route('/users/profile/image', methods=['POST'])
@login_required
def upload_profile_image():
    try:
        user_id = session.get('user_id')
        user = User.query.get_or_404(user_id)
        
        if 'image' not in request.files:
            return jsonify({"message": "未提供圖片"}), 400
            
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({"message": "未選擇圖片"}), 400
            
        # 檢查檔案類型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({"message": "不支援的檔案類型"}), 400
            
        # 產生唯一的檔案名稱
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 建立上傳路徑
        upload_folder = current_app.config['UPLOAD_FOLDER']
        profile_upload_path = os.path.join(upload_folder, 'profiles')
        
        # 確保資料夾存在
        if not os.path.exists(profile_upload_path):
            os.makedirs(profile_upload_path)
            
        # 儲存檔案
        file_path = os.path.join(profile_upload_path, unique_filename)
        file.save(file_path)
        
        # 更新資料庫中的頭像路徑
        user.profile_image = f"/uploads/profiles/{unique_filename}"
        user.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "頭像已更新",
            "profile_image": user.profile_image
        })
    except Exception as e:
        db.session.rollback()
        print(f"上傳頭像錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"message": f"上傳頭像失敗: {str(e)}"}), 500

# 修改密碼
@api_bp.route('/users/change-password', methods=['POST'])
@login_required
def change_password():
    try:
        user_id = session.get('user_id')
        user = User.query.get_or_404(user_id)
        
        data = request.get_json()
        
        # 檢查必要欄位
        if not all(key in data for key in ['current_password', 'new_password']):
            return jsonify({"message": "缺少必要欄位"}), 400
            
        # 驗證當前密碼
        if not user.check_password(data['current_password']):
            return jsonify({"message": "當前密碼不正確"}), 400
            
        # 檢查新密碼長度
        if len(data['new_password']) < 8:
            return jsonify({"message": "新密碼長度不足，至少需要8個字元"}), 400
            
        # 更新密碼
        user.password_hash = generate_password_hash(data['new_password'])
        user.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return jsonify({"message": "密碼已更新"})
    except Exception as e:
        db.session.rollback()
        print(f"更新密碼錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"message": f"更新密碼失敗: {str(e)}"}), 500

# 更新個人活動設置和通知偏好
@api_bp.route('/users/preferences', methods=['PUT'])
@login_required
def update_preferences():
    try:
        user_id = session.get('user_id')
        user = User.query.get_or_404(user_id)
        
        data = request.get_json()
        
        # 檢查是否有偏好設置欄位
        if not hasattr(user, 'preferences') or user.preferences is None:
            user.preferences = {}
            
        # 更新偏好設置
        for key, value in data.items():
            user.preferences[key] = value
            
        user.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "偏好設置已更新",
            "preferences": user.preferences
        })
    except Exception as e:
        db.session.rollback()
        print(f"更新偏好設置錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"message": f"更新偏好設置失敗: {str(e)}"}), 500

# 帳戶停用
@api_bp.route('/users/deactivate', methods=['POST'])
@login_required
def deactivate_account():
    try:
        user_id = session.get('user_id')
        user = User.query.get_or_404(user_id)
        
        data = request.get_json()
        
        # 確認用戶密碼
        if not user.check_password(data.get('password', '')):
            return jsonify({"message": "密碼不正確"}), 400
            
        # 標記帳戶為停用
        user.is_active = False
        user.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        # 清除 session
        session.clear()
        
        return jsonify({
            "message": "帳戶已停用"
        })
    except Exception as e:
        db.session.rollback()
        print(f"停用帳戶錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"message": f"停用帳戶失敗: {str(e)}"}), 500

# 帳戶刪除 (僅超級管理員可以實際刪除，一般用戶僅停用)
@api_bp.route('/users/delete', methods=['POST'])
@login_required
def delete_account():
    try:
        user_id = session.get('user_id')
        user = User.query.get_or_404(user_id)
        
        data = request.get_json()
        
        # 確認用戶密碼
        if not user.check_password(data.get('password', '')):
            return jsonify({"message": "密碼不正確"}), 400
            
        # 僅標記為已刪除，但不實際刪除
        user.is_active = False
        user.is_deleted = True
        user.deleted_at = datetime.datetime.utcnow()
        user.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        # 清除 session
        session.clear()
        
        return jsonify({
            "message": "帳戶已刪除"
        })
    except Exception as e:
        db.session.rollback()
        print(f"刪除帳戶錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"message": f"刪除帳戶失敗: {str(e)}"}), 500
    
# 取消Portal授權
@api_bp.route('/users/unbind-portal', methods=['POST'])
@login_required
def unbind_portal():
    try:
        user_id = session.get('user_id')
        user = User.query.get_or_404(user_id)
        
        if not user:
            return jsonify({
                "success": False,
                "message": "找不到用戶資訊"
            }), 404
        
        # 檢查用戶是否已綁定Portal
        if not user.portal_id:
            return jsonify({"message": "用戶未綁定Portal"}), 400
        
        # 解除綁定
        user.portal_id = None
        user.school_email = None
        user.is_verified = False
        user.updated_at = datetime.datetime.utcnow()

        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Portal授權已取消"
        })
    except Exception as e:
        db.session.rollback()
        print(f"取消Portal授權錯誤: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "message": f"取消Portal授權失敗: {str(e)}"
        }), 500