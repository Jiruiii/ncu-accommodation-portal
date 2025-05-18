import json
from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO
from app import socketio
from app.api import api_bp
from app.extensions import db
from app.models.chat import Message
from datetime import datetime

import logging
logging.basicConfig(level=logging.INFO)

messages = []

@api_bp.route('/chat', methods=["POST"])
def push_message():
    data = request.json # 解析 JSON 資料
    message = data.get("message") # 取的訊息內容
    time = data.get("time") # 取的訊息時間

    # 如果訊息為空則回傳錯誤
    if not message or not time:
        return jsonify({"error" : "缺少必要參數"}), 400

    chat_message = {"message": message, "time": time}
    messages.append(chat_message)

    # 存入資料庫
    #new_message = Message(sender_id=sender_id, receiver_id=receiver_id, message=message, time=time)
    #db.session.add(new_message)
    #db.session.commit()

    return jsonify({"status" : "訊息已儲存"}) # 回應成功訊息

@api_bp.route('/chat', methods=["GET"])
def get_message():
    #messages = Message.query.order_by(Message.message_time.desc()).all()  # 按時間排序
    #return jsonify([
    #    {"id": msg.message_id, "text": msg.message_text, "timestamp": msg.message_time.isoformat()}
    #    for msg in messages
    #])
    return jsonify(messages) # 回傳所有訊息


from flask_socketio import join_room as socketio_join_room
# 讓用戶加入專屬房間接收訊息
@socketio.on("join_room")
def handle_join_room(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)  # 若收到的是 JSON 字串則解析

        user_id = data.get("user_id")
        socketio_join_room(user_id)
        logging.info(f"User {user_id} 已加入房間")
    except json.JSONDecodeError:
        logging.info("錯誤: 接收到的 `data` 不是 JSON 格式")

# 發送訊息給特定用戶
@socketio.on("new_message")
def handle_private_message(data):
    sender_id = str(data["sender"])
    receiver_id = str(data["receiver"])  
    message = data["message"]
    time = data.get("time")

    print(f"User {sender_id} 發送訊息給 {receiver_id}: {message}")

    # 存入資料庫
    save_message(sender_id, receiver_id, message, time)

    socketio.emit("new_message", {"sender": sender_id, "message": message}, room=receiver_id)

# 存入訊息
def save_message(sender, receiver, message, time):
    new_message = Message(sender_id=sender, receiver_id=receiver, message=message, time=time)
    db.session.add(new_message)
    db.session.commit()

@api_bp.route('/chat/history', methods=["GET"])
def get_chat_history():
    sender_id = request.args.get("sender_id")
    receiver_id = request.args.get("receiver_id")

    messages = Message.query.filter(
        ((Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.sender_id == sender_id)) 
    ).order_by(Message.time.asc()).all()

    return jsonify([
        {"sender": msg.sender_id, "text": msg.message, "timestamp": msg.time.isoformat()}
        for msg in messages
    ])
