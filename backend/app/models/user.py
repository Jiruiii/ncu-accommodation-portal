from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    portal_id = db.Column(db.String(50), unique=True, nullable=True)  # 用於 Portal 登入
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    school_email = db.Column(db.String(100), unique=True, nullable=True)  # 學校郵箱
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    profile_image = db.Column(db.String(255))
    user_role = db.Column(db.Enum('student', 'landlord', 'admin', 'superuser',name='user_role_enum'), 
                          default='student', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_email_verified = db.Column(db.Boolean, default=False)
    is_phone_verified = db.Column(db.Boolean, default=False)
    
    # 關聯
    accommodations = db.relationship('Accommodation', foreign_keys='Accommodation.owner_id',
                                   backref='owner', lazy='dynamic')
    reviews = db.relationship('Review', foreign_keys='Review.reviewer_id',
                            backref='reviewer', lazy='dynamic')
    favorites = db.relationship('Favorite', foreign_keys='Favorite.user_id',
                              backref='user', lazy='dynamic', cascade='all, delete-orphan')
    tenant_leases = db.relationship('Lease', foreign_keys='Lease.tenant_id',
                                  backref='tenant', lazy='dynamic')
    landlord_leases = db.relationship('Lease', foreign_keys='Lease.landlord_id',
                                    backref='landlord', lazy='dynamic')
    sublets = db.relationship('Sublet', backref='poster', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.user_role in ['admin', 'superuser']
    
    def is_superuser(self):
        return self.user_role == 'superuser'
    
    def __repr__(self):
        return f'<User {self.username}>'

class VerificationCode(db.Model):
    __tablename__ = 'verification_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    code = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # email 或 phone
    target = db.Column(db.String(100), nullable=False)  # 郵箱或手機號
    expiry = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('verification_codes', lazy='dynamic'))

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    token = db.Column(db.String(100), nullable=False, unique=True)
    expiry = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('password_resets', lazy='dynamic'))
    
    def __repr__(self):
        return f"<PasswordReset id={self.id} user_id={self.user_id}>"