import json
import os
import sys
from datetime import datetime

# 將當前腳本目錄加入到路徑中，以便導入應用程式模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.accommodation import Accommodation, AccommodationImage, Amenity, AccommodationAmenity

def clear_tables(app):
    with app.app_context():
        # 先清空有外鍵約束的表格
        print("清空資料表...")
        
        # 先清空關聯表
        db.session.execute(db.text("DELETE FROM accommodation_amenities"))
        
        # 清空圖片表
        db.session.execute(db.text("DELETE FROM accommodation_images"))
        
        # 清空收藏表 (如果有的話)
        db.session.execute(db.text("DELETE FROM favorites"))
        
        # 清空設備表
        db.session.execute(db.text("DELETE FROM amenities"))
        
        # 最後清空房源表
        db.session.execute(db.text("DELETE FROM accommodations"))
        
        # 提交更改
        db.session.commit()
        print("所有表格已清空")

def import_data():
    # 創建應用程式實例
    app = create_app('development')
    
    clear_tables(app)  # 清空資料表
    
    with app.app_context():
        # 讀取 JSON 資料
        data_path = os.path.join(app.root_path, '..', '..', 'src', 'data.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            accommodations_data = json.load(f)
        
        # 遍歷並導入每個房源
        for data in accommodations_data:
            try:
                # 轉換房租格式 (例如 "每月 3000~4000 元" 轉為數字)
                rent_str = data.get('房租', '0')
                if isinstance(rent_str, str):
                    # 提取第一個數字
                    import re
                    numbers = re.findall(r'\d+', rent_str)
                    rent_price = int(numbers[0]) if numbers else 0
                else:
                    rent_price = int(rent_str)
                
                # 處理地址和區域
                address = data.get('地址', '地址不詳')
                district = None
                city = "桃園市"  # 默認城市
                
                # 嘗試從地址中提取區域
                if "區" in address:
                    # 找到最後一個"市"後面，第一個"區"之前的部分
                    if "市" in address:
                        city_parts = address.split("市")
                        if len(city_parts) > 1:
                            district_parts = city_parts[1].split("區")
                            if district_parts:
                                district = district_parts[0] + "區"
                    else:
                        district_parts = address.split("區")
                        if district_parts:
                            district = district_parts[0] + "區"
                
                # 獲取聯絡資訊
                contact_info = data.get('聯絡資訊', '').strip()
                
                # 分別處理套房和雅房的坪數
                studio_area = 0
                single_area = 0
                area = 0
                
                # 處理套房坪數
                if data.get('出租房數', {}).get('套房', {}).get('坪數'):
                    studio_area_str = data.get('出租房數', {}).get('套房', {}).get('坪數', '0')
                    studio_area_numbers = re.findall(r'\d+', studio_area_str)
                    if studio_area_numbers:
                        studio_area = float(studio_area_numbers[0])
                
                # 處理雅房坪數
                if data.get('出租房數', {}).get('雅房', {}).get('坪數'):
                    single_area_str = data.get('出租房數', {}).get('雅房', {}).get('坪數', '0')
                    single_area_numbers = re.findall(r'\d+', single_area_str)
                    if single_area_numbers:
                        single_area = float(single_area_numbers[0])
                
                # 總坪數可設為兩者的平均值或套房的坪數
                if studio_area > 0:
                    area = studio_area
                elif single_area > 0:
                    area = single_area
                
                # 獲取套房資訊
                studio_info = data.get('出租房數', {}).get('套房', {})
                studio_count = 0
                studio_available = 0
                if studio_info:
                    studio_count = int(studio_info.get('總數', 0) or 0)
                    studio_available = int(studio_info.get('空房', 0) or 0)
                
                # 獲取雅房資訊
                single_info = data.get('出租房數', {}).get('雅房', {})
                single_count = 0
                single_available = 0
                if single_info:
                    single_count = int(single_info.get('總數', 0) or 0)
                    single_available = int(single_info.get('空房', 0) or 0)
                
                # 確定房源類型
                property_type = 'apartment'  # 默認類型
                if studio_count > 0 and single_count == 0:
                    property_type = 'studio'
                elif single_count > 0 and studio_count == 0:
                    property_type = 'single_room'
                
                # 創建新的房源記錄
                accommodation = Accommodation(
                    owner_id=1,  # 如果沒有真實房東 ID，可以設定一個默認房東
                    title=data.get('標題', '無標題'),
                    description=', '.join(data.get('屋況說明', [])) if data.get('屋況說明') else None,
                    property_type=property_type,
                    rent_price=rent_price,
                    address=address,
                    city=city,
                    district=district,
                    
                    # 總房間數
                    room_count=studio_count + single_count,
                    
                    # 新增的欄位
                    studio_count=studio_count,
                    studio_available=studio_available,
                    single_count=single_count,
                    single_available=single_available,
                    
                    area=area,
                    studio_area=studio_area,
                    single_area=single_area,
                    status='available',  # 設置為可用狀態
                    
                    # 如果資料庫模型已新增 contact_info 欄位
                    contact_info=contact_info,
                    
                    # 其他費用處理
                    deposit=rent_price,  # 提取不到押金時，默認使用一個月房租
                )
                
                db.session.add(accommodation)
                db.session.flush()  # 獲取 ID
                
                # 儲存圖片
                for i, img_path in enumerate(data.get('房屋照片', [])):
                    # 從相對路徑轉為絕對路徑或網址
                    image = AccommodationImage(
                        accommodation_id=accommodation.accommodation_id,
                        image_url=img_path,  # 使用原始路徑，前端需要調整
                        is_primary=(i == 0)  # 第一張作為主圖
                    )
                    db.session.add(image)
                
                # 添加設備 - 避免重複添加
                # 使用集合去除重複項
                feature_set = set(data.get('屋內設備', []) + data.get('公共設施', []))
                
                for feature in feature_set:
                    # 檢查設備是否存在，不存在則創建
                    amenity = Amenity.query.filter_by(name=feature).first()
                    if not amenity:
                        amenity = Amenity(
                            name=feature,
                            category='appliance' if feature in data.get('屋內設備', []) else 'utility'
                        )
                        db.session.add(amenity)
                        db.session.flush()
                    
                    # 檢查該關聯是否已存在
                    existing_relation = AccommodationAmenity.query.filter_by(
                        accommodation_id=accommodation.accommodation_id,
                        amenity_id=amenity.amenity_id
                    ).first()
                    
                    # 只有當關聯不存在時才添加
                    if not existing_relation:
                        # 關聯設備與房源
                        accommodation_amenity = AccommodationAmenity(
                            accommodation_id=accommodation.accommodation_id,
                            amenity_id=amenity.amenity_id
                        )
                        db.session.add(accommodation_amenity)
                
                db.session.commit()
                print(f"成功導入: {data.get('標題', '無標題')}")
                
            except Exception as e:
                db.session.rollback()
                print(f"導入失敗: {data.get('標題', '無標題')} - {str(e)}")
                
    print("資料匯入完成")

if __name__ == "__main__":
    import_data()