from datetime import datetime
from app.extensions import db

class Sublet(db.Model):
    __tablename__ = 'sublets'
    
    sublet_id = db.Column(db.Integer, primary_key=True)
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodations.accommodation_id'), 
                               nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    original_price = db.Column(db.Numeric(10, 2))
    asking_price = db.Column(db.Numeric(10, 2), nullable=False)
    available_from = db.Column(db.Date, nullable=False)
    available_to = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('active', 'pending', 'fulfilled', 'expired', 'canceled',
                             name='sublet_status_enum'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Sublet {self.title}>'