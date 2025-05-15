from datetime import datetime
from app.extensions import db

class Review(db.Model):
    __tablename__ = 'reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodations.accommodation_id'), 
                               nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    overall_rating = db.Column(db.Numeric(2, 1), nullable=False)
    safety_rating = db.Column(db.Integer)
    cleanliness_rating = db.Column(db.Integer)
    landlord_rating = db.Column(db.Integer)
    value_rating = db.Column(db.Integer)
    location_rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Review {self.review_id}>'