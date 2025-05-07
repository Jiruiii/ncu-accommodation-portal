from datetime import datetime
from app.extensions import db

class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'
    
    request_id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey('leases.lease_id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.Enum('low', 'medium', 'high', 'emergency',
                              name='urgency_enum'), default='medium')
    status = db.Column(db.Enum('pending', 'approved', 'in_progress', 'resolved', 'rejected',
                             name='maintenance_status_enum'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    landlord_response = db.Column(db.Text)
    resolution_details = db.Column(db.Text)
    
    # 關聯
    images = db.relationship('MaintenanceImage', backref='maintenance_request', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MaintenanceRequest {self.title}>'


class MaintenanceImage(db.Model):
    __tablename__ = 'maintenance_images'
    
    image_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('maintenance_requests.request_id'), 
                         nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MaintenanceImage {self.image_id}>'