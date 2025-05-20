from datetime import datetime
from app.extensions import db
from sqlalchemy.sql import func # type: ignore
from sqlalchemy import event # type: ignore

class Topic(db.Model):
    """討論區主題表"""
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    is_pinned = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    
    # 關聯
    creator = db.relationship('User', backref=db.backref('topics', lazy='dynamic'))
    posts = db.relationship('Post', backref='topic', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'creator': self.creator.username if self.creator else None,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_pinned': self.is_pinned,
            'view_count': self.view_count,
            'post_count': self.posts.count()
        }


class Post(db.Model):
    """討論區文章表"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    is_pinned = db.Column(db.Boolean, default=False)
    
    # 關聯
    author = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))
    replies = db.relationship('Reply', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('PostLike', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'author': self.author.username if self.author else None,
            'author_id': self.author_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_pinned': self.is_pinned,
            'like_count': self.likes.count(),
            'reply_count': self.replies.count(),
            'likes': [like.user_id for like in self.likes.all()]
        }


class Reply(db.Model):
    """文章回覆表"""
    __tablename__ = 'replies'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 關聯
    author = db.relationship('User', backref=db.backref('replies', lazy='dynamic'))
    likes = db.relationship('ReplyLike', backref='reply', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'author': self.author.username if self.author else None,
            'author_id': self.author_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'like_count': self.likes.count(),
            'likes': [like.user_id for like in self.likes.all()]
        }


class PostLike(db.Model):
    """文章讚表"""
    __tablename__ = 'post_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # 確保每個使用者只能對一篇文章按一次讚
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_post_like'),)


class ReplyLike(db.Model):
    """回覆讚表"""
    __tablename__ = 'reply_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    reply_id = db.Column(db.Integer, db.ForeignKey('replies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # 確保每個使用者只能對一條回覆按一次讚
    __table_args__ = (db.UniqueConstraint('reply_id', 'user_id', name='unique_reply_like'),)


# 更新主題更新時間
@event.listens_for(Post, 'after_insert')
@event.listens_for(Post, 'after_update')
def update_topic_timestamp(mapper, connection, target):
    connection.execute(
        db.text(
            "UPDATE topics SET updated_at = current_timestamp WHERE id = :topic_id"
        ),
        {"topic_id": target.topic_id}
    )