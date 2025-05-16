import json
import importlib
import os
from datetime import datetime
from flask import current_app
from sqlalchemy import inspect # type: ignore
from app.extensions import db

# 將模型對象轉換為可序列化字典
def serialize_model(model):
    serialized = {}
    for column in inspect(model).mapper.column_attrs:
        value = getattr(model, column.key)
        # 處理日期和時間格式
        if isinstance(value, datetime):
            serialized[column.key] = value.isoformat()
        elif hasattr(value, '__dict__'):  # 如果是嵌套對象，不進行序列化
            continue
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
    
    # 將數據轉換為 JSON
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    
    # 如果指定了文件路徑，則保存到文件
    if filepath:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_data)
        return True
    
    # 否則返回 JSON 字符串
    return json_data

# 從 JSON 導入資料到資料庫
def import_db_from_json(filepath=None, json_data=None, clear_existing=False):
    """
    從 JSON 文件或字符串導入數據到資料庫
    
    Args:
        filepath: JSON 文件路徑
        json_data: JSON 字符串，與 filepath 二選一
        clear_existing: 是否清空現有數據
        
    Returns:
        成功導入的記錄數量
    """
    if filepath:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif json_data:
        data = json.loads(json_data)
    else:
        raise ValueError("必須提供 filepath 或 json_data 其中之一")
    
    # 獲取模型類映射
    models = {}
    models_module = importlib.import_module('app.models')
    
    for item_name in dir(models_module):
        item = getattr(models_module, item_name)
        if isinstance(item, type) and hasattr(item, '__tablename__'):
            models[item.__tablename__] = item
    
    # 記錄導入結果
    results = {'imported': 0, 'errors': 0, 'tables': {}}
    
    # 開始導入
    try:
        for table_name, records in data.items():
            # 跳過元數據
            if table_name.startswith('_'):
                continue
                
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
            
            # 導入記錄
            for record_data in records:
                try:
                    # 創建新記錄實例
                    record = model_class()
                    
                    # 設置屬性
                    for key, value in record_data.items():
                        # 跳過主鍵，由數據庫自動生成
                        if key == 'id' or key.endswith('_id'):
                            continue
                            
                        # 嘗試設置屬性
                        if hasattr(record, key):
                            setattr(record, key, value)
                    
                    # 添加到會話
                    db.session.add(record)
                    table_results['processed'] += 1
                    results['imported'] += 1
                except Exception as e:
                    current_app.logger.error(f"導入 {table_name} 記錄時出錯: {str(e)}")
                    table_results['errors'] += 1
                    results['errors'] += 1
            
            # 保存表結果
            results['tables'][table_name] = {
                'status': 'imported' if table_results['processed'] > 0 else 'error',
                'processed': table_results['processed'],
                'errors': table_results['errors']
            }
        
        # 提交事務
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"導入數據時出錯: {str(e)}")
        results['global_error'] = str(e)
    
    return results