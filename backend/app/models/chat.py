from app.extensions import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'chat_message'

    chat_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ChatMessage {self.chat_id}>'
