from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    notification_type = db.Column(db.Enum('system', 'lease', 'maintenance', 'message', 'review', 'other',
                                        name='notification_type_enum'), nullable=False)
    related_id = db.Column(db.Integer)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Notification {self.notification_id}>'