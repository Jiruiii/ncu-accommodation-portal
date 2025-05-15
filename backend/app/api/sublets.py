from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from app.api import api_bp
from app.models.sublet import Sublet
from app.models.accommodation import Accommodation
from app.models.user import User
from app.extensions import db
from datetime import datetime, date

@api_bp.route('/sublets', methods=['GET'])
def get_sublets():
    """獲取轉租房源列表，支援分頁和篩選"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    # 基本查詢
    query = Sublet.query.filter(Sublet.status.in_(['active', 'pending']))
    
    # 篩選條件
    if 'min_price' in request.args:
        query = query.filter(Sublet.asking_price >= request.args.get('min_price', type=float))
    if 'max_price' in request.args:
        query = query.filter(Sublet.asking_price <= request.args.get('max_price', type=float))
    if 'available_from' in request.args:
        try:
            available_from = datetime.strptime(request.args.get('available_from'), '%Y-%m-%d').date()
            query = query.filter(Sublet.available_from >= available_from)
        except ValueError:
            return jsonify({'message': '日期格式無效，請使用 YYYY-MM-DD 格式'}), 400
    if 'available_to' in request.args:
        try:
            available_to = datetime.strptime(request.args.get('available_to'), '%Y-%m-%d').date()
            query = query.filter(Sublet.available_to <= available_to)
        except ValueError:
            return jsonify({'message': '日期格式無效，請使用 YYYY-MM-DD 格式'}), 400
            
    # 排序
    sort_by = request.args.get('sort_by', 'created_at')
    if sort_by == 'price_low':
        query = query.order_by(Sublet.asking_price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Sublet.asking_price.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Sublet.available_from.asc())
    elif sort_by == 'date_desc':
        query = query.order_by(Sublet.available_from.desc())
    else:
        query = query.order_by(Sublet.created_at.desc())
    
    # 執行分頁查詢
    sublets = query.paginate(page=page, per_page=per_page)
    
    # 格式化結果
    result = {
        'items': [],
        'total': sublets.total,
        'pages': sublets.pages,
        'current_page': sublets.page
    }
    
    for sublet in sublets.items:
        # 獲取關聯住所資訊
        accommodation = sublet.accommodation
        
        result['items'].append({
            'id': sublet.sublet_id,
            'title': sublet.title,
            'asking_price': float(sublet.asking_price),
            'original_price': float(sublet.original_price) if sublet.original_price else None,
            'available_from': sublet.available_from.isoformat() if sublet.available_from else None,
            'available_to': sublet.available_to.isoformat() if sublet.available_to else None,
            'status': sublet.status,
            'accommodation': {
                'id': accommodation.accommodation_id,
                'title': accommodation.title,
                'address': accommodation.address,
                'property_type': accommodation.property_type,
                'room_count': accommodation.room_count,
                'bathroom_count': accommodation.bathroom_count
            },
            'poster': {
                'id': sublet.poster.user_id,
                'username': sublet.poster.username,
                'is_verified': sublet.poster.is_verified
            },
            'created_at': sublet.created_at.isoformat()
        })
    
    return jsonify(result), 200

@api_bp.route('/sublets/<int:id>', methods=['GET'])
def get_sublet_detail(id):
    """獲取轉租房源詳情"""
    sublet = Sublet.query.get_or_404(id)
    
    # 如果轉租房源不可用且不是擁有者查看，則拒絕訪問
    if sublet.status not in ['active', 'pending']:
        try:
            user_id = get_jwt_identity()
            if user_id != sublet.poster_id:
                return jsonify({'message': '此轉租房源不可用'}), 404
        except:
            return jsonify({'message': '此轉租房源不可用'}), 404
    
    # 獲取關聯住所資訊
    accommodation = sublet.accommodation
    
    # 獲取主要圖片
    images = []
    for image in accommodation.images:
        images.append({
            'id': image.image_id,
            'url': image.image_url,
            'is_primary': image.is_primary
        })
    
    # 返回詳細信息
    result = {
        'id': sublet.sublet_id,
        'title': sublet.title,
        'description': sublet.description,
        'asking_price': float(sublet.asking_price),
        'original_price': float(sublet.original_price) if sublet.original_price else None,
        'available_from': sublet.available_from.isoformat() if sublet.available_from else None,
        'available_to': sublet.available_to.isoformat() if sublet.available_to else None,
        'status': sublet.status,
        'accommodation': {
            'id': accommodation.accommodation_id,
            'title': accommodation.title,
            'address': accommodation.address,
            'district': accommodation.district,
            'property_type': accommodation.property_type,
            'room_count': accommodation.room_count,
            'bathroom_count': accommodation.bathroom_count,
            'area': accommodation.area,
            'is_furnished': accommodation.is_furnished,
            'has_water_bill': accommodation.has_water_bill,
            'has_electricity_bill': accommodation.has_electricity_bill,
            'has_internet': accommodation.has_internet,
            'images': images,
            'distance_to_university': accommodation.distance_to_university
        },
        'poster': {
            'id': sublet.poster.user_id,
            'username': sublet.poster.username,
            'email': sublet.poster.email if sublet.poster.email else None,
            'phone': sublet.poster.phone if sublet.poster.phone else None,
            'is_verified': sublet.poster.is_verified
        },
        'created_at': sublet.created_at.isoformat(),
        'updated_at': sublet.updated_at.isoformat(),
        'is_verified': sublet.is_verified
    }
    
    return jsonify(result), 200

@api_bp.route('/sublets', methods=['POST'])
@jwt_required()
def create_sublet():
    """新增轉租房源"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 檢查必要欄位
    required_fields = ['accommodation_id', 'title', 'asking_price', 'available_from', 'available_to']
    if not all(field in data for field in required_fields):
        return jsonify({'message': '缺少必要欄位'}), 400
    
    # 檢查轉租日期是否有效
    try:
        available_from = datetime.strptime(data['available_from'], '%Y-%m-%d').date()
        available_to = datetime.strptime(data['available_to'], '%Y-%m-%d').date()
        
        if available_from >= available_to:
            return jsonify({'message': '結束日期必須晚於開始日期'}), 400
        
        if available_from < date.today():
            return jsonify({'message': '開始日期不能早於今天'}), 400
    except ValueError:
        return jsonify({'message': '日期格式無效，請使用 YYYY-MM-DD 格式'}), 400
    
    # 檢查住所是否存在
    accommodation = Accommodation.query.get(data['accommodation_id'])
    if not accommodation:
        return jsonify({'message': '找不到指定的住所'}), 404
    
    # 檢查用戶是否有權限發布此轉租
    # 如果是管理員，則可以為任何住所發布轉租
    user = User.query.get(user_id)
    if user.user_role != 'admin':
        # 檢查是否是此住所的租客
        is_tenant = any(lease.tenant_id == user_id and lease.accommodation_id == accommodation.accommodation_id 
                        for lease in user.tenant_leases)
        
        # 如果不是租客也不是此住所的擁有者，則拒絕訪問
        if not is_tenant and accommodation.owner_id != user_id:
            return jsonify({'message': '您沒有權限為此住所發布轉租'}), 403
    
    # 創建新的轉租房源
    new_sublet = Sublet(
        accommodation_id=data['accommodation_id'],
        poster_id=user_id,
        title=data['title'],
        description=data.get('description', ''),
        original_price=data.get('original_price'),
        asking_price=data['asking_price'],
        available_from=available_from,
        available_to=available_to,
        status='pending'  # 預設為待審核狀態
    )
    
    db.session.add(new_sublet)
    db.session.commit()
    
    return jsonify({
        'message': '轉租房源新增成功，等待審核',
        'sublet_id': new_sublet.sublet_id
    }), 201

@api_bp.route('/sublets/<int:id>', methods=['PUT'])
@jwt_required()
def update_sublet(id):
    """更新轉租房源"""
    user_id = get_jwt_identity()
    sublet = Sublet.query.get_or_404(id)
    
    # 檢查是否是發布者或管理員
    user = User.query.get(user_id)
    if sublet.poster_id != user_id and user.user_role != 'admin':
        return jsonify({'message': '您沒有權限修改此轉租房源'}), 403
    
    # 檢查狀態是否允許修改
    if sublet.status not in ['active', 'pending']:
        return jsonify({'message': '此轉租房源狀態不允許修改'}), 400
    
    data = request.get_json()
    
    # 更新允許修改的欄位
    if 'title' in data:
        sublet.title = data['title']
    if 'description' in data:
        sublet.description = data['description']
    if 'asking_price' in data:
        sublet.asking_price = data['asking_price']
    
    # 更新日期需要驗證
    if 'available_from' in data:
        try:
            sublet.available_from = datetime.strptime(data['available_from'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': '日期格式無效，請使用 YYYY-MM-DD 格式'}), 400
    if 'available_to' in data:
        try:
            sublet.available_to = datetime.strptime(data['available_to'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': '日期格式無效，請使用 YYYY-MM-DD 格式'}), 400
    
    # 確保結束日期晚於開始日期
    if sublet.available_from >= sublet.available_to:
        return jsonify({'message': '結束日期必須晚於開始日期'}), 400
    
    # 管理員可以更新狀態
    if 'status' in data and user.user_role == 'admin':
        valid_statuses = ['active', 'pending', 'fulfilled', 'expired', 'canceled']
        if data['status'] in valid_statuses:
            sublet.status = data['status']
        else:
            return jsonify({'message': '無效的狀態值'}), 400
    
    # 更新時間戳
    sublet.updated_at = datetime.utcnow()
    
    # 如果非管理員修改，狀態重設為pending
    if user.user_role != 'admin':
        sublet.status = 'pending'
        sublet.is_verified = False
    
    db.session.commit()
    
    return jsonify({
        'message': '轉租房源更新成功',
        'sublet_id': sublet.sublet_id
    }), 200

@api_bp.route('/sublets/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_sublet(id):
    """刪除轉租房源"""
    user_id = get_jwt_identity()
    sublet = Sublet.query.get_or_404(id)
    
    # 檢查是否是發布者或管理員
    user = User.query.get(user_id)
    if sublet.poster_id != user_id and user.user_role != 'admin':
        return jsonify({'message': '您沒有權限刪除此轉租房源'}), 403
    
    db.session.delete(sublet)
    db.session.commit()
    
    return jsonify({
        'message': '轉租房源已刪除'
    }), 200

@api_bp.route('/sublets/<int:id>/verify', methods=['POST'])
@jwt_required()
def verify_sublet(id):
    """審核轉租房源（管理員專用）"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 檢查是否是管理員
    if user.user_role != 'admin':
        return jsonify({'message': '只有管理員可以審核轉租房源'}), 403
    
    sublet = Sublet.query.get_or_404(id)
    data = request.get_json()
    
    # 設置審核狀態
    is_approved = data.get('approve', False)
    reject_reason = data.get('reject_reason')
    
    if is_approved:
        sublet.status = 'active'
        sublet.is_verified = True
        message = '轉租房源已通過審核並發布'
    else:
        sublet.status = 'canceled'
        sublet.is_verified = False
        message = '轉租房源未通過審核'
    
    # 更新時間戳
    sublet.updated_at = datetime.utcnow()
    db.session.commit()
    
    # TODO: 後續可以加上通知功能，通知發布者審核結果
    
    return jsonify({
        'message': message,
        'sublet_id': sublet.sublet_id,
        'status': sublet.status,
        'reject_reason': reject_reason
    }), 200

@api_bp.route('/users/sublets', methods=['GET'])
@jwt_required()
def get_user_sublets():
    """獲取當前用戶發布的轉租房源"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    # 查詢用戶發布的所有轉租房源
    sublets = Sublet.query.filter_by(poster_id=user_id).order_by(
        Sublet.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    # 格式化結果
    result = {
        'items': [],
        'total': sublets.total,
        'pages': sublets.pages,
        'current_page': sublets.page
    }
    
    for sublet in sublets.items:
        accommodation = sublet.accommodation
        
        result['items'].append({
            'id': sublet.sublet_id,
            'title': sublet.title,
            'asking_price': float(sublet.asking_price),
            'original_price': float(sublet.original_price) if sublet.original_price else None,
            'available_from': sublet.available_from.isoformat() if sublet.available_from else None,
            'available_to': sublet.available_to.isoformat() if sublet.available_to else None,
            'status': sublet.status,
            'accommodation': {
                'id': accommodation.accommodation_id,
                'title': accommodation.title,
                'address': accommodation.address
            },
            'created_at': sublet.created_at.isoformat(),
            'is_verified': sublet.is_verified
        })
    
    return jsonify(result), 200

@api_bp.route('/sublets/admin', methods=['GET'])
@jwt_required()
def admin_get_sublets():
    """管理員獲取所有轉租房源（包括待審核）"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 檢查是否是管理員
    if user.user_role != 'admin':
        return jsonify({'message': '只有管理員可以訪問此端點'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    status = request.args.get('status')
    
    # 查詢條件
    query = Sublet.query
    
    # 按狀態篩選
    if status:
        query = query.filter_by(status=status)
    
    # 排序方式
    sort_by = request.args.get('sort_by', 'created_at')
    if sort_by == 'created_at':
        query = query.order_by(Sublet.created_at.desc())
    elif sort_by == 'updated_at':
        query = query.order_by(Sublet.updated_at.desc())
    
    # 執行分頁查詢
    sublets = query.paginate(page=page, per_page=per_page)
    
    # 格式化結果
    result = {
        'items': [],
        'total': sublets.total,
        'pages': sublets.pages,
        'current_page': sublets.page
    }
    
    for sublet in sublets.items:
        accommodation = sublet.accommodation
        poster = sublet.poster
        
        result['items'].append({
            'id': sublet.sublet_id,
            'title': sublet.title,
            'asking_price': float(sublet.asking_price),
            'available_from': sublet.available_from.isoformat() if sublet.available_from else None,
            'available_to': sublet.available_to.isoformat() if sublet.available_to else None,
            'status': sublet.status,
            'is_verified': sublet.is_verified,
            'accommodation': {
                'id': accommodation.accommodation_id,
                'title': accommodation.title,
                'address': accommodation.address
            },
            'poster': {
                'id': poster.user_id,
                'username': poster.username,
                'email': poster.email,
                'is_verified': poster.is_verified
            },
            'created_at': sublet.created_at.isoformat(),
            'updated_at': sublet.updated_at.isoformat()
        })
    
    return jsonify(result), 200

@api_bp.route('/accommodations/<int:id>/sublets', methods=['GET'])
def get_accommodation_sublets(id):
    """獲取特定住所的所有轉租"""
    # 檢查住所是否存在
    accommodation = Accommodation.query.get_or_404(id)
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    # 只顯示可用的轉租
    sublets = Sublet.query.filter_by(
        accommodation_id=id,
        status='active',
        is_verified=True
    ).order_by(Sublet.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # 格式化結果
    result = {
        'items': [],
        'total': sublets.total,
        'pages': sublets.pages,
        'current_page': sublets.page
    }
    
    for sublet in sublets.items:
        result['items'].append({
            'id': sublet.sublet_id,
            'title': sublet.title,
            'asking_price': float(sublet.asking_price),
            'original_price': float(sublet.original_price) if sublet.original_price else None,
            'available_from': sublet.available_from.isoformat() if sublet.available_from else None,
            'available_to': sublet.available_to.isoformat() if sublet.available_to else None,
            'poster': {
                'id': sublet.poster.user_id,
                'username': sublet.poster.username,
                'is_verified': sublet.poster.is_verified
            },
            'created_at': sublet.created_at.isoformat()
        })
    
    return jsonify(result), 200