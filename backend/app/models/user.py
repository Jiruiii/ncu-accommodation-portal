from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    portal_id = db.Column(db.String(50), unique=True, nullable=True)  # 用於 Portal 登入
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    profile_image = db.Column(db.String(255))
    user_role = db.Column(db.Enum('student', 'landlord', 'admin', name='user_role_enum'), 
                          default='student', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # 關聯
    accommodations = db.relationship('Accommodation', foreign_keys='Accommodation.owner_id',
                                   backref='owner', lazy='dynamic')
    reviews = db.relationship('Review', foreign_keys='Review.reviewer_id',
                            backref='reviewer', lazy='dynamic')
    favorites = db.relationship('Favorite', foreign_keys='Favorite.user_id',
                              backref='user', lazy='dynamic')
    student_verification = db.relationship('StudentVerification', backref='user', uselist=False)
    tenant_leases = db.relationship('Lease', foreign_keys='Lease.tenant_id',
                                  backref='tenant', lazy='dynamic')
    landlord_leases = db.relationship('Lease', foreign_keys='Lease.landlord_id',
                                    backref='landlord', lazy='dynamic')
    sublets = db.relationship('Sublet', backref='poster', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class StudentVerification(db.Model):
    __tablename__ = 'student_verifications'
    
    verification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    student_id = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100))
    year_of_study = db.Column(db.Integer)
    verification_document = db.Column(db.String(255))
    verified_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    verification_status = db.Column(db.Enum('pending', 'verified', 'rejected', 
                                          name='verification_status_enum'),
                                   default='pending')
    
    def __repr__(self):
        return f'<StudentVerification {self.student_id}>'