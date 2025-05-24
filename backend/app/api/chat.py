import json
import pytz
from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO # type: ignore
from app import socketio
from app.api import api_bp
from app.extensions import db
from app.models.chat import Message
from datetime import datetime

import logging
logging.basicConfig(level=logging.INFO)

from flask_socketio import join_room as socketio_join_room # type: ignore

# 分隔不同的聊天室
@socketio.on("join_room")
def handle_join_room(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)  # 若收到的是 JSON 字串則解析

        user_id = data.get("user_id")
        socketio_join_room(user_id) # 讓用戶加入指定的 WebSocket 房間

        logging.info(f"User {user_id} 已加入房間")

    except json.JSONDecodeError:
        logging.info("錯誤: 接收到的 `data` 不是 JSON 格式")

# 發送訊息給特定用戶
@socketio.on("new_message")
def handle_private_message(data):
    sender_id = str(data["sender"])
    receiver_id = str(data["receiver"])  
    message = data["message"]
    time_str = data.get("time")

    tz = pytz.timezone("Asia/Taipei")  # 設定台灣時區

    # 將 ISO 時間字串轉為 datetime 物件
    if time_str:
        try:
            time = datetime.fromisoformat(time_str.replace("Z", "+00:00")).astimezone(tz)
        except ValueError:
            time = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz)
    else:
        time = datetime.utcnow()

    # 格式化時間
    taiwan_time = time.astimezone(pytz.timezone("Asia/Taipei"))
    formatted_time = taiwan_time.strftime("%p %I:%M")
    formatted_time = formatted_time.replace("AM", "上午").replace("PM", "下午")

    logging.info(f"User {sender_id} 發送訊息給 {receiver_id}: {message}")

    # 存入資料庫
    new_message = Message(sender_id=sender_id, receiver_id=receiver_id, message=message, time=time)
    db.session.add(new_message)
    db.session.commit()

    socketio.emit("new_message", {
        "sender": sender_id,
        "receiver": receiver_id,
        "message": message,
        "time": formatted_time
    }, room=str(receiver_id))

# 存入訊息
def save_message(sender, receiver, message, time):
    new_message = Message(sender_id=sender, receiver_id=receiver, message=message, time=time)
    db.session.add(new_message)
    db.session.commit()

from sqlalchemy import or_, and_

@api_bp.route('/chat/history', methods=["GET"])
def get_chat_history():
    sender_id = int(request.args.get("sender_id", 0))
    receiver_id = int(request.args.get("receiver_id", 0))

    # 從資料庫中找出符合條件的訊息
    messages = Message.query.filter(
        or_(
            Message.sender_id == sender_id,
            Message.receiver_id == sender_id
        )
    ).order_by(Message.time).all() # 訊息案時間排序
    
    return jsonify([
        {
            "sender": msg.sender_id, 
            "receiver": msg.receiver_id,
            "text": msg.message, 
            "timestamp": msg.time.isoformat()}
        for msg in messages
    ])
