import json
import importlib
import os
from datetime import datetime, date
from decimal import Decimal
from flask import current_app
from sqlalchemy import inspect # type: ignore
from app.extensions import db

# 自定義 JSON 編碼器，處理特殊類型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # 處理 Decimal 類型
        if isinstance(obj, Decimal):
            return float(obj)
        
        # 處理日期和時間類型
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        # 其他特殊類型處理可以在這裡添加
        
        # 默認行為
        return super().default(obj)

# 將模型對象轉換為可序列化字典
def serialize_model(model):
    serialized = {}
    for column in inspect(model).mapper.column_attrs:
        value = getattr(model, column.key)
        
        # 處理不同類型的值
        if value is None:
            serialized[column.key] = None
        # 處理日期和時間格式
        elif isinstance(value, (datetime, date)):
            serialized[column.key] = value.isoformat()
        # 處理 Decimal 類型
        elif isinstance(value, Decimal):
            serialized[column.key] = float(value)
        # 如果是嵌套對象，不進行序列化
        elif hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool)):
            continue
        # 處理其他基本類型
        else:
            serialized[column.key] = value
            
    return serialized

# 將資料庫導出為 JSON
def export_db_to_json(filepath=None):
    """
    將資料庫中的數據導出為 JSON 格式
    
    Args:
        filepath: JSON 文件保存路徑，如果為 None，則返回 JSON 字符串
        
    Returns:
        如果指定了 filepath，則返回 True 表示成功；否則返回 JSON 字符串
    """
    data = {}
    
    # 按照表名動態查找所有模型類
    models_module = importlib.import_module('app.models')
    model_classes = []
    
    # 獲取所有模型類
    for item_name in dir(models_module):
        item = getattr(models_module, item_name)
        if isinstance(item, type) and hasattr(item, '__tablename__'):
            model_classes.append(item)
    
    # 導出每個模型的數據
    for model_class in model_classes:
        table_name = model_class.__tablename__
        records = model_class.query.all()
        data[table_name] = [serialize_model(record) for record in records]
    
    # 添加元數據
    data['_metadata'] = {
        'exported_at': datetime.now().isoformat(),
        'tables': list(data.keys())
    }
    
    # 將數據轉換為 JSON，使用自定義編碼器
    json_data = json.dumps(data, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)
    
    # 如果指定了文件路徑，則保存到文件
    if filepath:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_data)
        return True
    
    # 否則返回 JSON 字符串
    return json_data

# 從 JSON 導入資料到資料庫
def import_db_from_json(filepath=None, json_data=None, clear_existing=False, update_existing=True):
    """
    從 JSON 文件或字符串導入數據到資料庫
    
    Args:
        filepath: JSON 文件路徑
        json_data: JSON 字符串，與 filepath 二選一
        clear_existing: 是否清空現有數據
        update_existing: 是否更新已存在的記錄
        
    Returns:
        導入結果統計
    """
    if filepath:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif json_data:
        data = json.loads(json_data)
    else:
        raise ValueError("必須提供 filepath 或 json_data 其中之一")
    
    # 獲取模型類映射
    models = get_models_mapping()
    
    # 記錄導入結果
    results = {'imported': 0, 'errors': 0, 'tables': {}}
    
    # 開始導入
    try:
        # 設定表格導入順序，先導入基本表格，再導入相依表格
        table_order = [
            "users",             # 用戶表通常是基礎表格
            "amenities",         # 設施表通常無外鍵依賴
            "accommodations",    # 房源表依賴用戶表
            "accommodation_amenities",  # 依賴房源表和設施表
            "accommodation_images",     # 依賴房源表
            "reviews",           # 依賴用戶表和房源表
            "favorites",         # 依賴用戶表和房源表
            "sublets",           # 可能依賴用戶表和房源表
            "leases",            # 依賴用戶表和房源表
            "maintenance_requests",     # 依賴用戶表和房源表
            "maintenance_images",       # 依賴維修請求表
            "fraud_reports",     # 依賴用戶表和房源表
            "chat_message",      # 依賴用戶表
            "messages",          # 備選表名
            "comments",          # 依賴用戶表和房源表
            "replies",           # 依賴評論表和用戶表
            "comment_likes",     # 依賴評論表和用戶表
            "reply_likes",       # 依賴回覆表和用戶表
            "notifications",     # 依賴用戶表
            "verification_codes",  # 依賴用戶表
            "password_resets"    # 依賴用戶表
        ]
        
        # 先處理有順序要求的表格
        for table_name in table_order:
            if table_name in data and isinstance(data[table_name], list) and len(data[table_name]) > 0:
                # 檢查表名是否有對應的模型
                if table_name not in models:
                    current_app.logger.warning(f"找不到表 {table_name} 對應的模型類")
                    results['tables'][table_name] = {'status': 'skipped', 'reason': 'no_model'}
                    continue
                
                model_class = models[table_name]
                table_results = {'processed': 0, 'errors': 0}
                
                # 如果需要清空現有數據
                if clear_existing:
                    model_class.query.delete()
                    db.session.commit()
                
                # 檢查表的主鍵列
                inspector = inspect(db.engine)
                try:
                    pk_columns = inspector.get_pk_constraint(table_name)['constrained_columns']
                except:
                    # 如果無法獲取主鍵信息，使用默認的 'id' 或表名+'_id'
                    pk_columns = ['id'] if hasattr(model_class, 'id') else [f"{table_name[:-1]}_id"]
                
                # 導入記錄
                for record_data in data[table_name]:
                    try:
                        # 檢查是否包含所有主鍵
                        has_all_pks = True
                        pk_values = {}
                        for pk in pk_columns:
                            if pk not in record_data or record_data[pk] is None:
                                # 相容性處理: 如果是 user_id 但有 _id
                                if pk == 'user_id' and '_id' in record_data:
                                    record_data['user_id'] = record_data['_id']
                                # 相容性處理: 如果是 id 但有 xxx_id
                                elif pk == 'id' and f"{table_name[:-1]}_id" in record_data:
                                    record_data['id'] = record_data[f"{table_name[:-1]}_id"]
                                else:
                                    has_all_pks = False
                                    break
                            else:
                                pk_values[pk] = record_data[pk]
                        
                        # 如果缺少主鍵，跳過這條記錄
                        if not has_all_pks:
                            current_app.logger.warning(f"跳過缺少主鍵的記錄: {record_data}")
                            table_results['errors'] += 1
                            continue
                        
                        # 查詢是否已存在相同主鍵的記錄
                        filter_conditions = []
                        for pk, value in pk_values.items():
                            filter_conditions.append(getattr(model_class, pk) == value)
                        
                        existing_record = None
                        if filter_conditions:
                            existing_record = model_class.query.filter(*filter_conditions).first()
                        
                        # 篩選有效的欄位
                        valid_data = {}
                        for key, value in record_data.items():
                            # 特殊處理 '_id' 轉 'id' 或 'table_id'
                            mapped_key = key
                            if key == '_id':
                                if hasattr(model_class, 'id'):
                                    mapped_key = 'id'
                                elif hasattr(model_class, f"{table_name[:-1]}_id"):
                                    mapped_key = f"{table_name[:-1]}_id"
                            
                            # 確保該欄位存在於模型中
                            if hasattr(model_class, mapped_key):
                                # 處理特殊類型
                                attr = getattr(model_class, mapped_key)
                                if hasattr(attr, 'type') and hasattr(attr.type, 'python_type'):
                                    column_type = attr.type.python_type
                                    if column_type == Decimal and isinstance(value, (int, float)):
                                        value = Decimal(str(value))
                                    elif column_type == datetime and isinstance(value, str):
                                        try:
                                            value = datetime.fromisoformat(value)
                                        except:
                                            pass
                                
                                valid_data[mapped_key] = value
                        
                        # 如果記錄已存在且更新模式開啟，則更新現有記錄
                        if existing_record and update_existing and not clear_existing:
                            for key, value in valid_data.items():
                                setattr(existing_record, key, value)
                            
                            # 更新會話
                            db.session.add(existing_record)
                            table_results['processed'] += 1
                            results['imported'] += 1
                        elif not existing_record:
                            # 直接使用參數創建模型實例
                            record = model_class(**valid_data)
                            
                            # 添加到會話
                            db.session.add(record)
                            table_results['processed'] += 1
                            results['imported'] += 1
                        
                        # 每處理 50 筆記錄提交一次，避免事務過大
                        if table_results['processed'] % 50 == 0:
                            db.session.flush()
                            
                    except Exception as e:
                        current_app.logger.error(f"導入 {table_name} 記錄時出錯: {str(e)}")
                        table_results['errors'] += 1
                        results['errors'] += 1
                
                # 每個表格導入完成後提交一次
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"提交 {table_name} 資料時出錯: {str(e)}")
                    table_results['errors'] += len(data[table_name])
                    results['errors'] += len(data[table_name])
                    results['imported'] -= table_results['processed']
                    table_results['processed'] = 0
                
                # 保存表結果
                results['tables'][table_name] = {
                    'status': 'imported' if table_results['processed'] > 0 else 'error',
                    'processed': table_results['processed'],
                    'errors': table_results['errors']
                }
                
                current_app.logger.info(f"表 {table_name} 匯入完成: {table_results['processed']} 筆成功, {table_results['errors']} 筆失敗")
        
        # 處理未在順序列表中的表格
        for table_name, records in data.items():
            if table_name not in table_order and not table_name.startswith('_') and isinstance(records, list) and len(records) > 0:
                # 檢查表名是否有對應的模型
                if table_name not in models:
                    current_app.logger.warning(f"找不到表 {table_name} 對應的模型類")
                    results['tables'][table_name] = {'status': 'skipped', 'reason': 'no_model'}
                    continue
                
                # 這裡應該實現與上面相同的處理邏輯
                # 為避免程式碼重複，您可以將處理表格的邏輯抽取到一個單獨的函數中
                
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"導入數據時出錯: {str(e)}")
        results['global_error'] = str(e)
    
    return results

def get_models_mapping():
    """獲取表格名稱到模型類的映射"""
    from app.models.user import User, VerificationCode, PasswordReset
    from app.models.accommodation import (
        Accommodation, AccommodationImage, Amenity, 
        AccommodationAmenity, Favorite
    )
    from app.models.review import Review
    from app.models.sublet import Sublet
    from app.models.lease import Lease
    from app.models.maintenance import MaintenanceRequest, MaintenanceImage
    from app.models.notification import Notification
    from app.models.fraud import FraudReport
    from app.models.chat import Message
    from app.models.comments import Comment, Reply, CommentLike, ReplyLike, Report
    
    # 建立表格名稱到模型類的映射
    return {
        'users': User,
        'verification_codes': VerificationCode,
        'password_resets': PasswordReset,
        'accommodations': Accommodation,
        'accommodation_images': AccommodationImage,
        'amenities': Amenity,
        'accommodation_amenities': AccommodationAmenity,
        'favorites': Favorite,
        'reviews': Review,
        'sublets': Sublet,
        'leases': Lease,
        'maintenance_requests': MaintenanceRequest,
        'maintenance_images': MaintenanceImage,
        'notifications': Notification,
        'fraud_reports': FraudReport,
        'messages': Message,  # 注意檢查實際表名是否為 'messages' 或 'chat_messages'
        'chat_message': Message,  # 備選表名
        'comments': Comment,
        'replies': Reply,
        'comment_likes': CommentLike,
        'reply_likes': ReplyLike,
        'reports': Report
    }