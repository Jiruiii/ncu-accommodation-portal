from datetime import datetime
from app.extensions import db

class Accommodation(db.Model):
    __tablename__ = 'accommodations'
    
    accommodation_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    property_type = db.Column(db.Enum('apartment', 'studio', 'house', 
                                    'shared_room', 'single_room',
                                    name='property_type_enum'), nullable=False)
    room_count = db.Column(db.Integer) # 房間總數
    studio_count = db.Column(db.Integer)  # 套房總數
    studio_available = db.Column(db.Integer)  # 套房空房數
    single_count = db.Column(db.Integer)  # 雅房總數
    single_available = db.Column(db.Integer)  # 雅房空房數
    contact_info = db.Column(db.String(255), nullable=False)
    bathroom_count = db.Column(db.Integer)
    area = db.Column(db.Float)
    studio_area = db.Column(db.Float)  # 套房面積
    single_area = db.Column(db.Float)  # 雅房面積
    rent_price = db.Column(db.Numeric(10, 2), nullable=False)
    deposit = db.Column(db.Numeric(10, 2))
    is_furnished = db.Column(db.Boolean, default=False)
    has_water_bill = db.Column(db.Boolean, default=False)
    has_electricity_bill = db.Column(db.Boolean, default=False)
    has_internet = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(50))
    district = db.Column(db.String(50))
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    distance_to_university = db.Column(db.Float)
    available_from = db.Column(db.Date)
    minimum_stay = db.Column(db.Integer)
    maximum_stay = db.Column(db.Integer)
    status = db.Column(db.Enum('available', 'pending', 'rented', 'unavailable',
                             name='accommodation_status_enum'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verified = db.Column(db.DateTime)
    
    # 關聯
    images = db.relationship('AccommodationImage', backref='accommodation', lazy='dynamic',
                           cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='accommodation', lazy='dynamic',
                            cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='accommodation', lazy='dynamic',
                              cascade='all, delete-orphan')
    leases = db.relationship('Lease', backref='accommodation', lazy='dynamic')
    sublets = db.relationship('Sublet', backref='accommodation', lazy='dynamic')
    amenities = db.relationship('Amenity', secondary='accommodation_amenities',
                              backref=db.backref('accommodations', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Accommodation {self.title}>'


class AccommodationImage(db.Model):
    __tablename__ = 'accommodation_images'
    
    image_id = db.Column(db.Integer, primary_key=True)
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodations.accommodation_id'), 
                               nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AccommodationImage {self.image_id}>'


class Amenity(db.Model):
    __tablename__ = 'amenities'
    
    amenity_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.Enum('appliance', 'furniture', 'security', 'utility', 'other',
                               name='amenity_category_enum'))
    
    def __repr__(self):
        return f'<Amenity {self.name}>'


class AccommodationAmenity(db.Model):
    __tablename__ = 'accommodation_amenities'
    
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodations.accommodation_id'), 
                               primary_key=True)
    amenity_id = db.Column(db.Integer, db.ForeignKey('amenities.amenity_id'), 
                         primary_key=True)


class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodations.accommodation_id'), 
                               primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Favorite user_id={self.user_id} accommodation_id={self.accommodation_id}>'