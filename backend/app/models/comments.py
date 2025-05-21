from datetime import datetime
from app.extensions import db
from sqlalchemy.sql import func # type: ignore
from sqlalchemy import event # type: ignore

class Comment(db.Model):
    """房源評論表"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, nullable=False)  # 房源ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 評分 1-5
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 關聯
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    replies = db.relationship('Reply', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('CommentLike', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'user_id': self.user_id,
            'userName': self.user.username if self.user else None,
            'content': self.content,
            'rating': self.rating,
            'date': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'likes': self.likes.count(),
            'replyCount': self.replies.count(),
            'likedBy': [like.user_id for like in self.likes.all()]
        }


class Reply(db.Model):
    """評論回覆表"""
    __tablename__ = 'replies'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 關聯
    user = db.relationship('User', backref=db.backref('replies', lazy='dynamic'))
    likes = db.relationship('ReplyLike', backref='reply', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'comment_id': self.comment_id,
            'user_id': self.user_id,
            'author': self.user.username if self.user else None,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'like_count': self.likes.count(),
            'likes': [like.user_id for like in self.likes.all()]
        }


class CommentLike(db.Model):
    """評論讚表"""
    __tablename__ = 'comment_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # 確保每個使用者只能對一條評論按一次讚
    __table_args__ = (db.UniqueConstraint('comment_id', 'user_id', name='unique_comment_like'),)


class ReplyLike(db.Model):
    """回覆讚表"""
    __tablename__ = 'reply_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    reply_id = db.Column(db.Integer, db.ForeignKey('replies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # 確保每個使用者只能對一條回覆按一次讚
    __table_args__ = (db.UniqueConstraint('reply_id', 'user_id', name='unique_reply_like'),)