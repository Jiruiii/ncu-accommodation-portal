from app import create_app
from app.extensions import db
from sqlalchemy import inspect # type: ignore
import os
import time
from datetime import datetime

# 導入所有模型
from app.models.user import User, VerificationCode, PasswordReset
from app.models.accommodation import (
    Accommodation, AccommodationImage, Amenity, 
    AccommodationAmenity, Favorite
)
from app.models.review import Review
from app.models.comments import Comment, Reply, CommentLike, ReplyLike, Report
from app.models.chat import Message
from app.models.notification import Notification
from app.models.fraud import FraudReport
from app.models.lease import Lease
from app.models.maintenance import MaintenanceRequest, MaintenanceImage
from app.models.sublet import Sublet

# 定義要檢查的所有模型和表格名稱
MODEL_TABLES = [
    (User, 'users'),
    (VerificationCode, 'verification_codes'),
    (PasswordReset, 'password_resets'),
    (Accommodation, 'accommodations'),
    (AccommodationImage, 'accommodation_images'),
    (Amenity, 'amenities'),
    (AccommodationAmenity, 'accommodation_amenities'),
    (Favorite, 'favorites'),
    (Review, 'reviews'),
    (Comment, 'comments'),
    (Reply, 'replies'),
    (CommentLike, 'comment_likes'),
    (ReplyLike, 'reply_likes'),
    (Report, 'reports'),
    (Message, 'chat_message'),
    (Notification, 'notifications'),
    (FraudReport, 'fraud_reports'),
    (Lease, 'leases'),
    (MaintenanceRequest, 'maintenance_requests'),
    (MaintenanceImage, 'maintenance_images'),
    (Sublet, 'sublets')
]

def create_backup(db_path):
    """建立資料庫備份"""
    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f"app_{timestamp}.db")
    
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"已建立資料庫備份: {backup_path}")
        return True
    else:
        print(f"警告: 資料庫檔案不存在，無法建立備份")
        return False

def create_all_tables():
    """確保所有表格存在"""
    app = create_app()
    
    # 資料庫路徑
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    
    # 先建立備份
    create_backup(db_path)
    
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print(f"資料庫中現有表格: {len(existing_tables)} 個")
        
        # 檢查哪些表格不存在
        missing_tables = []
        for model, table_name in MODEL_TABLES:
            if table_name not in existing_tables:
                missing_tables.append((model, table_name))
        
        if not missing_tables:
            print("所有必要的表格都已存在！")
            return True
        
        # 建立缺失的表格
        print(f"發現 {len(missing_tables)} 個缺失的表格，開始創建...")
        for model, table_name in missing_tables:
            try:
                print(f"創建表格: {table_name}...")
                model.__table__.create(db.engine, checkfirst=True)
                print(f"表格 {table_name} 已成功創建！")
            except Exception as e:
                print(f"創建表格 {table_name} 時出錯: {str(e)}")
        
        # 再次檢查
        after_tables = inspector.get_table_names()
        print(f"操作後資料庫中的表格: {len(after_tables)} 個")
        
        # 檢查是否還有缺失的表格
        still_missing = []
        for _, table_name in missing_tables:
            if table_name not in inspector.get_table_names():
                still_missing.append(table_name)
        
        if still_missing:
            print(f"警告: 仍有 {len(still_missing)} 個表格未能創建: {', '.join(still_missing)}")
            return False
        else:
            print("所有缺失的表格已成功創建！")
            return True

def verify_tables_structure():
    """檢查表格結構是否與模型一致"""
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        issues = []
        
        for model, table_name in MODEL_TABLES:
            if table_name not in inspector.get_table_names():
                issues.append(f"表格 {table_name} 不存在")
                continue
            
            # 獲取模型中定義的欄位
            model_columns = {c.name: c for c in model.__table__.columns}
            
            # 獲取資料庫中的欄位
            db_columns = {c['name']: c for c in inspector.get_columns(table_name)}
            
            # 檢查缺失的欄位
            for col_name in model_columns:
                if col_name not in db_columns:
                    issues.append(f"表格 {table_name} 缺少欄位 {col_name}")
        
        if issues:
            print("發現表格結構問題:")
            for issue in issues:
                print(f" - {issue}")
            return False
        else:
            print("所有表格結構與模型一致！")
            return True

if __name__ == "__main__":
    print("開始確保所有表格存在...")
    start_time = time.time()
    
    success = create_all_tables()
    if success:
        print("所有表格已創建，現在驗證表格結構...")
        verify_tables_structure()
    
    end_time = time.time()
    print(f"操作完成，耗時 {end_time - start_time:.2f} 秒")