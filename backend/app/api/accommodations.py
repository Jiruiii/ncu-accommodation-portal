import os
import datetime
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from werkzeug.utils import secure_filename
from app.api import api_bp
from app.models.accommodation import Accommodation, AccommodationImage, Favorite
from app.models.user import User
from app.extensions import db

def allowed_file(filename):
    """檢查檔案是否為允許的類型"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

@api_bp.route('/accommodations', methods=['GET'])
def get_accommodations():
    """獲取房源列表，支持分頁和過濾"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    # 基本查詢
    query = Accommodation.query.filter(Accommodation.status == 'available')
    
    # 篩選條件
    if 'min_price' in request.args:
        query = query.filter(Accommodation.rent_price >= request.args.get('min_price', type=float))
    if 'max_price' in request.args:
        query = query.filter(Accommodation.rent_price <= request.args.get('max_price', type=float))
    if 'property_type' in request.args:
        query = query.filter(Accommodation.property_type == request.args.get('property_type'))
    if 'min_room_count' in request.args:
        query = query.filter(Accommodation.room_count >= request.args.get('min_room_count', type=int))
    if 'furnished' in request.args:
        is_furnished = request.args.get('furnished').lower() == 'true'
        query = query.filter(Accommodation.is_furnished == is_furnished)
    if 'max_distance' in request.args and 'distance_to_university' in request.args:
        max_distance = request.args.get('max_distance', type=float)
        query = query.filter(Accommodation.distance_to_university <= max_distance)
    
    # 排序
    sort_by = request.args.get('sort_by', 'updated_at')
    if sort_by == 'price_low':
        query = query.order_by(Accommodation.rent_price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Accommodation.rent_price.desc())
    elif sort_by == 'newest':
        query = query.order_by(Accommodation.created_at.desc())
    else:
        query = query.order_by(Accommodation.updated_at.desc())
    
    # 執行分頁查詢
    accommodations = query.paginate(page=page, per_page=per_page)
    
    # 格式化結果
    result = {
        'items': [],
        'total': accommodations.total,
        'pages': accommodations.pages,
        'current_page': accommodations.page
    }
    
    for acc in accommodations.items:
        # 獲取主要圖片
        primary_image = AccommodationImage.query.filter_by(
            accommodation_id=acc.accommodation_id, is_primary=True
        ).first()
        
        image_url = primary_image.image_url if primary_image else None
        
        result['items'].append({
            'id': acc.accommodation_id,
            'title': acc.title,
            'property_type': acc.property_type,
            'rent_price': float(acc.rent_price),
            'deposit': float(acc.deposit) if acc.deposit else None,
            'address': acc.address,
            'district': acc.district,
            'room_count': acc.room_count,
            'bathroom_count': acc.bathroom_count,
            'area': acc.area,
            'distance_to_university': acc.distance_to_university,
            'image_url': image_url,
            'updated_at': acc.updated_at.isoformat()
        })
    
    return jsonify(result), 200

@api_bp.route('/accommodations', methods=['POST'])
@jwt_required()
def create_accommodation():
    """新增房源"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.user_role not in ['landlord', 'admin']:
        return jsonify({'message': '只有房東或管理員可以新增房源'}), 403
    
    data = request.form
    
    # 檢查必要欄位
    required_fields = ['title', 'property_type', 'rent_price', 'address']
    if not all(field in data for field in required_fields):
        return jsonify({'message': '缺少必要欄位'}), 400
    
    # 創建新房源
    new_acc = Accommodation(
        owner_id=user_id,
        title=data['title'],
        property_type=data['property_type'],
        rent_price=float(data['rent_price']),
        address=data['address'],
        description=data.get('description'),
        room_count=int(data['room_count']) if 'room_count' in data else None,
        bathroom_count=int(data['bathroom_count']) if 'bathroom_count' in data else None,
        area=float(data['area']) if 'area' in data else None,
        is_furnished=data.get('is_furnished', '').lower() == 'true',
        has_water_bill=data.get('has_water_bill', '').lower() == 'true',
        has_electricity_bill=data.get('has_electricity_bill', '').lower() == 'true',
        has_internet=data.get('has_internet', '').lower() == 'true',
        city=data.get('city'),
        district=data.get('district'),
        latitude=float(data['latitude']) if 'latitude' in data else None,
        longitude=float(data['longitude']) if 'longitude' in data else None,
        distance_to_university=float(data['distance_to_university']) if 'distance_to_university' in data else None,
        available_from=data.get('available_from'),
        status='pending'  # 預設為等待審核狀態
    )
    
    db.session.add(new_acc)
    db.session.commit()
    
    # 處理上傳的圖片
    if 'images' in request.files:
        images = request.files.getlist('images')
        for i, file in enumerate(images):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = int(datetime.utcnow().timestamp())
                new_filename = f"{new_acc.accommodation_id}_{timestamp}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
                file.save(file_path)
                
                # 存儲圖片路徑到資料庫
                image = AccommodationImage(
                    accommodation_id=new_acc.accommodation_id,
                    image_url=f"/static/uploads/{new_filename}",
                    is_primary=i == 0  # 第一張為主圖
                )
                db.session.add(image)
        
        db.session.commit()
    
    return jsonify({
        'message': '房源新增成功，等待審核',
        'accommodation_id': new_acc.accommodation_id
    }), 201

@api_bp.route('/accommodations/<int:id>', methods=['GET'])
def get_accommodation_detail(id):
    """獲取房源詳情"""
    acc = Accommodation.query.get_or_404(id)
    
    # 如果房源不可用且不是擁有者查看，則拒絕訪問
    if acc.status != 'available':
        try:
            user_id = get_jwt_identity()
            if user_id != acc.owner_id:
                return jsonify({'message': '此房源不可用'}), 404
        except:
            return jsonify({'message': '此房源不可用'}), 404
    
    # 獲取所有圖片
    images = [
        {'id': img.image_id, 'url': img.image_url, 'is_primary': img.is_primary}
        for img in acc.images
    ]
    
    # 獲取設施
    amenities = [
        {'id': a.amenity_id, 'name': a.name, 'category': a.category}
        for a in acc.amenities
    ]
    
    # 格式化結果
    result = {
        'id': acc.accommodation_id,
        'title': acc.title,
        'description': acc.description,
        'property_type': acc.property_type,
        'room_count': acc.room_count,
        'bathroom_count': acc.bathroom_count,
        'area': acc.area,
        'rent_price': float(acc.rent_price),
        'deposit': float(acc.deposit) if acc.deposit else None,
        'is_furnished': acc.is_furnished,
        'has_water_bill': acc.has_water_bill,
        'has_electricity_bill': acc.has_electricity_bill,
        'has_internet': acc.has_internet,
        'address': acc.address,
        'city': acc.city,
        'district': acc.district,
        'latitude': float(acc.latitude) if acc.latitude else None,
        'longitude': float(acc.longitude) if acc.longitude else None,
        'distance_to_university': acc.distance_to_university,
        'available_from': acc.available_from.isoformat() if acc.available_from else None,
        'images': images,
        'amenities': amenities,
        'owner': {
            'id': acc.owner.user_id,
            'name': f"{acc.owner.first_name} {acc.owner.last_name}" if acc.owner.first_name and acc.owner.last_name else acc.owner.username,
            'is_verified': acc.owner.is_verified
        },
        'created_at': acc.created_at.isoformat(),
        'updated_at': acc.updated_at.isoformat(),
        'last_verified': acc.last_verified.isoformat() if acc.last_verified else None
    }
    
    # 如果已登入，檢查是否已收藏
    try:
        user_id = get_jwt_identity()
        is_favorited = Favorite.query.filter_by(
            user_id=user_id, accommodation_id=id
        ).first() is not None
        result['is_favorited'] = is_favorited
    except:
        result['is_favorited'] = False
    
    return jsonify(result), 200