import os
import datetime
from flask import request, jsonify, current_app, session
from werkzeug.utils import secure_filename
from app.api import api_bp
from app.models.accommodation import Accommodation, AccommodationImage, Favorite
from functools import wraps
from app.models.user import User
from app.extensions import db

# 用戶身份驗證裝飾器
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "請先登入"}), 401
        
        return f(*args, **kwargs)
    return decorated

def allowed_file(filename):
    """檢查檔案是否為允許的類型"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

@api_bp.route('/accommodations', methods=['GET'])
def get_accommodations():
    """獲取所有可用的房源列表"""
    try:
        # 獲取查詢參數
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        sort_by = request.args.get('sort_by', 'newest')
        
        # 準備查詢
        query = Accommodation.query.filter_by(status='available')
        
        # 應用排序
        if sort_by == 'price_low':
            query = query.order_by(Accommodation.rent_price.asc())
        elif sort_by == 'price_high':
            query = query.order_by(Accommodation.rent_price.desc())
        elif sort_by == 'distance':
            query = query.order_by(Accommodation.distance_to_university.asc())
        else:  # newest
            query = query.order_by(Accommodation.created_at.desc())
        
        # 分頁
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        accommodations = pagination.items
        
        # 格式化結果
        result = []
        for acc in accommodations:
            # 獲取房源圖片
            images = AccommodationImage.query.filter_by(accommodation_id=acc.accommodation_id).all()
            image_urls = [{"id": img.image_id, "url": img.image_url, "is_primary": img.is_primary} for img in images]
            
            # 獲取設備
            amenities = []
            for amenity in acc.amenities:
                amenities.append({
                    "id": amenity.amenity_id,
                    "name": amenity.name,
                    "category": amenity.category
                })
                
            room_info = {
                "studio": {
                    "total": acc.studio_count or 0,
                    "available": acc.studio_available or 0,
                    "area": float(acc.studio_area) if acc.studio_area else (float(acc.area) if acc.area else None)
                },
                "single": {
                    "total": acc.single_count or 0,
                    "available": acc.single_available or 0,
                    "area": float(acc.single_area) if acc.single_area else (float(acc.area) if acc.area else None)
                }
            }
            
            # 房源基本信息
            acc_data = {
                "accommodation_id": acc.accommodation_id,
                "owner_id": acc.owner_id,
                "title": acc.title,
                "description": acc.description,
                "property_type": acc.property_type,
                "rent_price": float(acc.rent_price),
                "deposit": float(acc.deposit) if acc.deposit else None,
                "address": acc.address,
                "district": acc.district,
                "city": acc.city,
                "room_count": acc.room_count,
                "bathroom_count": acc.bathroom_count,
                "studio_count": acc.studio_count,
                "studio_available": acc.studio_available,
                "single_count": acc.single_count,
                "single_available": acc.single_available,
                "contact_info": acc.contact_info,
                "area": float(acc.area) if acc.area else None,
                "studio_area": float(acc.studio_area) if acc.studio_area else None,
                "single_area": float(acc.single_area) if acc.single_area else None,
                "distance_to_university": acc.distance_to_university,
                "images": image_urls,
                "amenities": amenities,
                "room_info": room_info,
                "is_furnished": acc.is_furnished,
                "has_water_bill": acc.has_water_bill,
                "has_electricity_bill": acc.has_electricity_bill,
                "has_internet": acc.has_internet,
                "created_at": acc.created_at.isoformat(),
                "updated_at": acc.updated_at.isoformat() if acc.updated_at else None
            }
            
            result.append(acc_data)
        
        # 返回結果
        return jsonify({
            "success": True,
            "items": result,
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"獲取房源列表時出錯: {str(e)}")
        return jsonify({
            "success":False,
            "message": "獲取房源列表時發生錯誤"
        }), 500

@api_bp.route('/accommodations', methods=['POST'])
@login_required
def create_accommodation():
    """新增房源"""
    user_id = session.get('user_id')
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
            user_id = session.get('user_id')
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
        'studio_count': acc.studio_count,
        'studio_available': acc.studio_available,
        'single_count': acc.single_count,
        'single_available': acc.single_available,
        'contact_info': acc.contact_info,
        'area': acc.area,
        'studio_area': float(acc.studio_area) if acc.studio_area else None,
        'single_area': float(acc.single_area) if acc.single_area else None,
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
        'room_info': {
            'studio': {
                'total': acc.studio_count or 0,
                'available': acc.studio_available or 0,
                'area': float(acc.studio_area) if acc.studio_area else (float(acc.area) if acc.area else None)
            },
            'single': {
                'total': acc.single_count or 0,
                'available': acc.single_available or 0,
                'area': float(acc.single_area) if acc.single_area else (float(acc.area) if acc.area else None)
            }
        },
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
        user_id = session.get('user_id')
        is_favorited = Favorite.query.filter_by(
            user_id=user_id, accommodation_id=id
        ).first() is not None
        result['is_favorited'] = is_favorited
    except:
        result['is_favorited'] = False
    
    return jsonify(result), 200

@api_bp.route('/accommodations/favorites', methods=['GET'])
@login_required
def get_favorites():
    """獲取當前用戶的所有收藏"""
    user_id = session.get('user_id')
    favorites = db.session.query(Favorite, Accommodation).join(
        Accommodation, Favorite.accommodation_id == Accommodation.accommodation_id
    ).filter(Favorite.user_id == user_id).all()
    
    # 格式化結果
    result = []
    for favorite, accommodation in favorites:
        # 獲取主要圖片
        primary_image = AccommodationImage.query.filter_by(
            accommodation_id=accommodation.accommodation_id, is_primary=True
        ).first()
        
        image_url = primary_image.image_url if primary_image else None
        
        result.append({
            'id': accommodation.accommodation_id,
            'title': accommodation.title,
            'property_type': accommodation.property_type,
            'rent_price': float(accommodation.rent_price),
            'deposit': float(accommodation.deposit) if accommodation.deposit else None,
            'address': accommodation.address,
            'district': accommodation.district,
            'room_count': accommodation.room_count,
            'bathroom_count': accommodation.bathroom_count,
            'area': accommodation.area,
            'distance_to_university': accommodation.distance_to_university,
            'image_url': image_url,
            'created_at': favorite.created_at.isoformat(),
            'is_favorited': True
        })
    
    return jsonify(result), 200

@api_bp.route('/accommodations/favorites/<int:accommodation_id>', methods=['POST'])
@login_required
def add_favorite(accommodation_id):
    """將房源加入收藏"""
    user_id = session.get('user_id')
    
    # 檢查房源是否存在
    accommodation = Accommodation.query.get(accommodation_id)
    if not accommodation:
        return jsonify({
            'success': False,
            'message': '該房源不存在'
        }), 404
    
    # 檢查是否已經收藏
    existing_favorite = Favorite.query.filter_by(
        user_id=user_id, accommodation_id=accommodation_id
    ).first()
    
    if existing_favorite:
        return jsonify({
            'success': False,
            'message': '已經收藏過此房源'
        }), 400
    
    # 新增收藏
    new_favorite = Favorite(
        user_id=user_id,
        accommodation_id=accommodation_id
    )
    
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({
        'success': True,    
        'message': '成功添加到收藏',
        'is_favorited': True,
        'favorite_id': {
            'user_id': user_id,
            'accommodation_id': accommodation_id
        }
    }), 201
    
@api_bp.route('/accommodations/favorites/delete/<int:accommodation_id>', methods=['POST'])
@login_required
def remove_favorite(accommodation_id):
    """從收藏中移除房源"""
    user_id = session.get('user_id')
    
    # 檢查收藏是否存在
    favorite = Favorite.query.filter_by(
        user_id=user_id, accommodation_id=accommodation_id
    ).first()
    
    if not favorite:
        return jsonify({
            'success': False,
            'message': '該房源未被收藏'
        }), 404
    
    # 刪除收藏
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '成功從收藏中移除',
        'is_favorited': False
    }), 200
    
@api_bp.route('/accommodations/favorites/toggle/<int:accommodation_id>', methods=['POST'])
@login_required
def toggle_favorite(accommodation_id):
    """切換收藏狀態"""
    user_id = session.get('user_id')
    
    # 檢查房源是否存在
    accommodation = Accommodation.query.get(accommodation_id)
    if not accommodation:
        return jsonify({
            'success': False,
            'message': '該房源不存在'
        }), 404
    
    # 檢查是否已經收藏
    existing_favorite = Favorite.query.filter_by(
        user_id=user_id, accommodation_id=accommodation_id
    ).first()
    
    if existing_favorite:
        # 已經收藏，則刪除
        db.session.delete(existing_favorite)
        db.session.commit()
        is_favorited = False
    else:
        # 未收藏，則新增
        new_favorite = Favorite(
            user_id=user_id,
            accommodation_id=accommodation_id
        )
        
        db.session.add(new_favorite)
        db.session.commit()
        is_favorited = True
    
    return jsonify({
        'success': True,
        'message': '成功切換收藏狀態',
        'is_favorited': is_favorited
    }), 200
    
@api_bp.route('/accommodations/favorites/status/<int:accommodation_id>', methods=['GET'])
@login_required
def check_favorite_status(accommodation_id):
    """檢查房源是否被收藏"""
    user_id = session.get('user_id')
    
    # 檢查是否已收藏
    existing = Favorite.query.filter_by(
        user_id=user_id, accommodation_id=accommodation_id
    ).first()
    
    return jsonify({
        'success': True,
        'is_favorited': existing is not None
    }), 200