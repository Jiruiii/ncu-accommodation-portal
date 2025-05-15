from datetime import datetime
from app.extensions import db

class FraudReport(db.Model):
    __tablename__ = 'fraud_reports'
    
    report_id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodations.accommodation_id'))
    sublet_id = db.Column(db.Integer, db.ForeignKey('sublets.sublet_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    reason = db.Column(db.Enum('scam', 'fake_listing', 'misleading_info', 'illegal_activity', 'other',
                             name='fraud_reason_enum'), nullable=False)
    description = db.Column(db.Text)
    evidence_urls = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'investigating', 'resolved', 'rejected',
                             name='fraud_status_enum'), default='pending')
    admin_comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # 關聯
    reporter = db.relationship('User', foreign_keys=[reporter_id], 
                             backref=db.backref('fraud_reports', lazy='dynamic'))
    reported_user = db.relationship('User', foreign_keys=[user_id], 
                                  backref=db.backref('reported_frauds', lazy='dynamic'))
    reported_accommodation = db.relationship('Accommodation', 
                                          backref=db.backref('fraud_reports', lazy='dynamic'))
    reported_sublet = db.relationship('Sublet', 
                                    backref=db.backref('fraud_reports', lazy='dynamic'))
    
    def __repr__(self):
        return f'<FraudReport {self.report_id}>'