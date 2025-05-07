from datetime import datetime
from app.extensions import db

class Lease(db.Model):
    __tablename__ = 'leases'
    
    lease_id = db.Column(db.Integer, primary_key=True)
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodations.accommodation_id'), 
                               nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False)
    deposit_amount = db.Column(db.Numeric(10, 2))
    lease_document = db.Column(db.String(255))
    status = db.Column(db.Enum('active', 'expired', 'terminated', 'renewal_pending',
                             name='lease_status_enum'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    maintenance_requests = db.relationship('MaintenanceRequest', backref='lease', lazy='dynamic',
                                         cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Lease {self.lease_id}>'