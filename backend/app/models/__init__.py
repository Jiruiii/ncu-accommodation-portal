# 導入所有模型以便於在 Flask shell 中使用
from app.models.user import User
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