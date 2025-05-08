from flask import request, jsonify, current_app, session
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt # type: ignore
from app.api import api_bp
from app.models.user import User
from app.models.accommodation import Accommodation, AccommodationImage
from app.models.review import Review
from app.models.sublet import Sublet
from app.models.lease import Lease
from app.extensions import db
from sqlalchemy import inspect, text # type: ignore
from functools import wraps
import datetime
import traceback

# 管理員身份驗證裝飾器
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "請先登入"}), 401
        
        # 獲取用戶
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user or not user.is_admin():
            return jsonify({"message": "需要管理員權限"}), 403
        
        return f(*args, **kwargs)
    return decorated

# 超級管理員身份驗證裝飾器
def superuser_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "請先登入"}), 401
        
        # 獲取用戶
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user or not user.is_superuser():
            return jsonify({"message": "需要超級管理員權限"}), 403
        
        return f(*args, **kwargs)
    return decorated

# 獲取所有資料表名稱
@api_bp.route('/admin/tables', methods=['GET'])
@admin_required
def get_tables():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    return jsonify({"tables": tables}), 200

# 獲取資料表結構
@api_bp.route('/admin/tables/<table_name>/structure', methods=['GET'])
@admin_required
def get_table_structure(table_name):
    inspector = inspect(db.engine)
    # 檢查表是否存在
    if table_name not in inspector.get_table_names():
        return jsonify({"message": "表格不存在"}), 404
    
    columns = inspector.get_columns(table_name)
    column_info = []
    for column in columns:
        column_data = {
            "name": column["name"],
            "type": str(column["type"]),
            "nullable": column.get("nullable", True),
            "default": str(column.get("default", "")) if column.get("default") is not None else None,
            "primary_key": column.get("primary_key", False)
        }
        column_info.append(column_data)
    
    return jsonify({
        "table_name": table_name,
        "columns": column_info
    }), 200

# 獲取表數據 (分頁)
@api_bp.route('/admin/tables/<table_name>/data', methods=['GET'])
@admin_required
def get_table_data(table_name):
    inspector = inspect(db.engine)
    if table_name not in inspector.get_table_names():
        return jsonify({"message": "表格不存在"}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    sort_by = request.args.get('sort_by')
    sort_direction = request.args.get('sort_direction', 'asc')
    
    # 構建查詢
    query = f"SELECT * FROM {table_name}"
    
    # 添加排序
    if sort_by:
        query += f" ORDER BY {sort_by} {sort_direction}"
    
    # 添加分頁
    query += f" LIMIT {per_page} OFFSET {(page-1)*per_page}"
    
    # 執行查詢
    result = db.session.execute(text(query)).fetchall()
    
    # 獲取總行數
    count_query = f"SELECT COUNT(*) AS count FROM {table_name}"
    total = db.session.execute(text(count_query)).scalar()
    
    # 處理數據（將日期等轉換為適合 JSON 的格式）
    rows = []
    for row in result:
        processed_row = {}
        for key, value in row._mapping.items():
            if isinstance(value, (datetime.date, datetime.datetime)):
                processed_row[key] = value.isoformat()
            else:
                processed_row[key] = value
        rows.append(processed_row)
    
    return jsonify({
        "data": rows,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page  # 計算總頁數
    }), 200

# 更新表數據（單行）
@api_bp.route('/admin/tables/<table_name>/data/<int:row_id>', methods=['PUT'])
@admin_required
def update_table_row(table_name, row_id):
    inspector = inspect(db.engine)
    if table_name not in inspector.get_table_names():
        return jsonify({"message": "表格不存在"}), 404
    
    data = request.get_json()
    
    # 獲取主鍵列名
    pk_column = None
    for column in inspector.get_columns(table_name):
        if column.get('primary_key', False):
            pk_column = column['name']
            break
    
    if not pk_column:
        return jsonify({"message": "找不到主鍵列"}), 400
    
    # 構建更新查詢
    set_clauses = []
    params = {}
    
    for key, value in data.items():
        # 跳過主鍵字段
        if key == pk_column:
            continue
        set_clauses.append(f"{key} = :{key}")
        params[key] = value
    
    # 添加 WHERE 條件
    params[pk_column] = row_id
    
    query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {pk_column} = :{pk_column}"
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
        return jsonify({"message": "數據已更新"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"更新失敗: {str(e)}"}), 400

# 刪除表數據（單行）
@api_bp.route('/admin/tables/<table_name>/data/<int:row_id>', methods=['DELETE'])
@admin_required
def delete_table_row(table_name, row_id):
    inspector = inspect(db.engine)
    if table_name not in inspector.get_table_names():
        return jsonify({"message": "表格不存在"}), 404
    
    # 獲取主鍵列名
    pk_column = None
    for column in inspector.get_columns(table_name):
        if column.get('primary_key', False):
            pk_column = column['name']
            break
    
    if not pk_column:
        return jsonify({"message": "找不到主鍵列"}), 400
    
    # 構建刪除查詢
    query = f"DELETE FROM {table_name} WHERE {pk_column} = :id"
    
    try:
        db.session.execute(text(query), {"id": row_id})
        db.session.commit()
        return jsonify({"message": "數據已刪除"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"刪除失敗: {str(e)}"}), 400

# 添加表數據
@api_bp.route('/admin/tables/<table_name>/data', methods=['POST'])
@admin_required
def add_table_row(table_name):
    inspector = inspect(db.engine)
    if table_name not in inspector.get_table_names():
        return jsonify({"message": "表格不存在"}), 404
    
    data = request.get_json()
    
    # 獲取所有列名
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    
    # 過濾有效的列
    valid_columns = []
    values = []
    params = {}
    
    for key, value in data.items():
        if key in columns:
            valid_columns.append(key)
            values.append(f":{key}")
            params[key] = value
    
    if not valid_columns:
        return jsonify({"message": "沒有有效的列數據"}), 400
    
    # 構建插入查詢
    query = f"INSERT INTO {table_name} ({', '.join(valid_columns)}) VALUES ({', '.join(values)})"
    
    try:
        result = db.session.execute(text(query), params)
        db.session.commit()
        
        # 在 SQLite 中獲取新插入的 ID
        last_id_query = "SELECT last_insert_rowid()"
        last_id = db.session.execute(text(last_id_query)).scalar()
        
        return jsonify({
            "message": "數據已添加", 
            "id": last_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"添加失敗: {str(e)}"}), 400

# 常用統計數據概覽
@api_bp.route('/admin/dashboard', methods=['GET'])
@admin_required
def get_dashboard_data():
    user_count = User.query.count()
    accommodation_count = Accommodation.query.count()
    review_count = Review.query.count()
    sublet_count = Sublet.query.count()
    
    # 最近注冊用戶
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_users_data = [
        {
            "id": user.user_id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "role": user.user_role
        }
        for user in recent_users
    ]
    
    # 最近添加的住所
    recent_accommodations = Accommodation.query.order_by(Accommodation.created_at.desc()).limit(5).all()
    recent_accommodations_data = [
        {
            "id": acc.accommodation_id,
            "title": acc.title,
            "address": acc.address,
            "created_at": acc.created_at.isoformat() if acc.created_at else None
        }
        for acc in recent_accommodations
    ]
    
    # 最近添加的轉租
    recent_sublets = Sublet.query.order_by(Sublet.created_at.desc()).limit(5).all()
    recent_sublets_data = [
        {
            "id": sublet.sublet_id,
            "title": sublet.title,
            "status": sublet.status,
            "created_at": sublet.created_at.isoformat() if sublet.created_at else None
        }
        for sublet in recent_sublets
    ]
    
    return jsonify({
        "counts": {
            "users": user_count,
            "accommodations": accommodation_count,
            "reviews": review_count,
            "sublets": sublet_count,
        },
        "recent_data": {
            "users": recent_users_data,
            "accommodations": recent_accommodations_data,
            "sublets": recent_sublets_data
        }
    }), 200
    
# 獲取用戶列表
@api_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    try:
        # 獲取參數
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_direction = request.args.get('sort_direction', 'desc')
        search = request.args.get('search', '')
        
        # 構建查詢
        query = User.query
        
        # 添加搜索條件
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    User.username.like(search_term),
                    User.email.like(search_term),
                )
            )
        
        # 添加排序
        if sort_direction == 'desc':
            query = query.order_by(db.desc(getattr(User, sort_by, User.created_at)))
        else:
            query = query.order_by(getattr(User, sort_by, User.created_at))
        
        # 分頁
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 格式化結果
        users = []
        for user in pagination.items:
            users.append({
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "user_role": user.user_role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "portal_id": user.portal_id if hasattr(user, 'portal_id') else None,
                "has_portal_id": bool(user.portal_id) if hasattr(user, 'portal_id') else False
            })
        
        return jsonify({
            "items": users,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "next_num": pagination.next_num,
            "prev_num": pagination.prev_num
        })
        
    except Exception as e:
        # 捕獲並記錄所有錯誤
        print(f"獲取用戶數據錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"message": f"系統錯誤: {str(e)}"}), 500    
        
# 獲取單個用戶
@api_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'profile_image': user.profile_image,
        'user_role': user.user_role,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'is_verified': user.is_verified,
        'is_active': user.is_active,
        'portal_id': user.portal_id
    })

# 更新用戶
@api_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # 更新用戶資料
    if 'username' in data:
        # 檢查用戶名是否已存在
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.user_id != user_id:
            return jsonify({'message': '此用戶名已被使用'}), 400
        user.username = data['username']
    
    if 'email' in data:
        # 檢查郵箱是否已存在
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.user_id != user_id:
            return jsonify({'message': '此郵箱已被使用'}), 400
        user.email = data['email']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    if 'user_role' in data:
        user.user_role = data['user_role']
    
    if 'phone' in data:
        user.phone = data['phone']
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    if 'is_verified' in data:
        user.is_verified = data['is_verified']
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': '用戶更新成功',
        'user_id': user.user_id
    })

# 刪除用戶
@api_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # 檢查是否嘗試刪除自己
    current_user_id = session.get('user_id')
    if user_id == current_user_id:
        return jsonify({'message': '不能刪除當前登入的用戶'}), 400
    
    # 刪除用戶
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'message': '用戶已刪除'
    })
    
@api_bp.route('/auth/check', methods=['GET'])
@jwt_required(optional=True)
def check_auth():
    """檢查認證狀態 - 診斷用"""
    try:
        # 獲取用戶 ID (如果已認證)
        user_id = get_jwt_identity()
        
        # 獲取 Authorization 標頭
        auth_header = request.headers.get('Authorization', '')
        
        # 收集診斷信息
        headers = {key: value for key, value in request.headers.items()}
        
        return jsonify({
            "authenticated": user_id is not None,
            "user_id": user_id,
            "auth_header": auth_header,
            "request_headers": headers,
            "jwt_config": {
                "secret_key": "hidden",
                "algorithm": current_app.config.get('JWT_ALGORITHM', '未設置'),
                "token_location": current_app.config.get('JWT_TOKEN_LOCATION', '未設置'),
                "header_name": current_app.config.get('JWT_HEADER_NAME', '未設置'),
                "header_type": current_app.config.get('JWT_HEADER_TYPE', '未設置'),
            }
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500