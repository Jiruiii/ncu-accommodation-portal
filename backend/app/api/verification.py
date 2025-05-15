from flask import jsonify, request, session
from app.models import User, VerificationCode
from app.extensions import db
from app.utils.email import send_email
from app.utils.sms import send_sms
from app.api import api_bp
import random
import string
import datetime
import traceback

# 生成驗證碼
def generate_code(length=6):
    """生成指定長度的數字驗證碼"""
    return ''.join(random.choice(string.digits) for _ in range(length))

@api_bp.route('/verification/send-email', methods=['POST'])
def send_email_verification():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': '請提供電子郵件'}), 400
    
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '請先登入'}), 401
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '找不到用戶資訊'}), 404
        
        # 檢查是否與用戶綁定的郵箱匹配
        if user.email != email:
            return jsonify({'success': False, 'message': '您只能驗證與您帳號綁定的電子郵件'}), 400
        
        # 生成驗證碼
        code = generate_code()
        
        # 檢查是否有舊的驗證碼，有則刪除
        old_code = VerificationCode.query.filter_by(user_id=user_id, type='email').first()
        if old_code:
            db.session.delete(old_code)
        
        # 儲存新的驗證碼
        expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)  # 10分鐘有效期
        verification = VerificationCode(
            user_id=user_id,
            code=code,
            type='email',
            target=email,
            expiry=expiry
        )
        db.session.add(verification)
        db.session.commit()
        
        # 發送驗證郵件
        email_subject = "中央大學校外外宿網 - 您的電子郵件驗證碼"
        email_body = f"""
        <p>親愛的 {user.username}：</p>
        <p>您好！感謝您使用中央大學校外外宿網。</p>
        <p>您的電子郵件驗證碼是：<strong style="font-size: 20px; color: #4a90e2;">{code}</strong></p>
        <p>此驗證碼將在 10 分鐘後失效，請及時驗證。</p>
        <p>如果這不是您的操作，請忽略此郵件。</p>
        <p>祝您使用愉快！<br>中央大學校外外宿網團隊</p>
        """
        
        send_email(email, email_subject, email_body)
        
        return jsonify({'success': True, 'message': '驗證碼已發送至您的電子郵件'})
        
    except Exception as e:
        db.session.rollback()
        print(f"發送電子郵件驗證碼失敗: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'發送失敗: {str(e)}'}), 500

@api_bp.route('/verification/send-phone', methods=['POST'])
def send_phone_verification():
    data = request.json
    phone = data.get('phone')
    
    if not phone:
        return jsonify({'success': False, 'message': '請提供手機號碼'}), 400
    
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '請先登入'}), 401
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '找不到用戶資訊'}), 404
        
        # 檢查是否與用戶綁定的手機匹配
        if user.phone != phone:
            return jsonify({'success': False, 'message': '您只能驗證與您帳號綁定的手機號碼'}), 400
        
        # 生成驗證碼
        code = generate_code()
        
        # 檢查是否有舊的驗證碼，有則刪除
        old_code = VerificationCode.query.filter_by(user_id=user_id, type='phone').first()
        if old_code:
            db.session.delete(old_code)
        
        # 儲存新的驗證碼
        expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)  # 10分鐘有效期
        verification = VerificationCode(
            user_id=user_id,
            code=code,
            type='phone',
            target=phone,
            expiry=expiry
        )
        db.session.add(verification)
        db.session.commit()
        
        # 發送簡訊
        message = f"【中央大學校外外宿網】您的手機驗證碼是：{code}，10分鐘內有效。請勿告知他人。"
        send_sms(phone, message)
        
        return jsonify({'success': True, 'message': '驗證碼已發送至您的手機'})
        
    except Exception as e:
        db.session.rollback()
        print(f"發送簡訊驗證碼失敗: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'發送失敗: {str(e)}'}), 500

@api_bp.route('/verification/verify-email', methods=['POST'])
def verify_email():
    data = request.json
    code = data.get('code')
    
    if not code:
        return jsonify({'success': False, 'message': '請提供驗證碼'}), 400
    
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '請先登入'}), 401
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '找不到用戶資訊'}), 404
        
        # 檢查驗證碼
        verification = VerificationCode.query.filter_by(
            user_id=user_id, 
            type='email',
            code=code
        ).first()
        
        if not verification:
            return jsonify({'success': False, 'message': '驗證碼錯誤'}), 400
            
        # 檢查是否過期
        if verification.expiry < datetime.datetime.utcnow():
            db.session.delete(verification)
            db.session.commit()
            return jsonify({'success': False, 'message': '驗證碼已過期，請重新獲取'}), 400
        
        # 更新用戶資訊
        user.is_email_verified = True
        
        # 刪除已使用的驗證碼
        db.session.delete(verification)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '電子郵件驗證成功',
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'is_email_verified': user.is_email_verified
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"驗證電子郵件失敗: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'驗證失敗: {str(e)}'}), 500

@api_bp.route('/verification/verify-phone', methods=['POST'])
def verify_phone():
    data = request.json
    code = data.get('code')
    
    if not code:
        return jsonify({'success': False, 'message': '請提供驗證碼'}), 400
    
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '請先登入'}), 401
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '找不到用戶資訊'}), 404
        
        # 檢查驗證碼
        verification = VerificationCode.query.filter_by(
            user_id=user_id, 
            type='phone',
            code=code
        ).first()
        
        if not verification:
            return jsonify({'success': False, 'message': '驗證碼錯誤'}), 400
            
        # 檢查是否過期
        if verification.expiry < datetime.datetime.utcnow():
            db.session.delete(verification)
            db.session.commit()
            return jsonify({'success': False, 'message': '驗證碼已過期，請重新獲取'}), 400
        
        # 更新用戶資訊
        user.is_phone_verified = True
        
        # 刪除已使用的驗證碼
        db.session.delete(verification)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '手機驗證成功',
            'user': {
                'user_id': user.user_id,
                'phone': user.phone,
                'is_phone_verified': user.is_phone_verified
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"驗證手機失敗: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'驗證失敗: {str(e)}'}), 500