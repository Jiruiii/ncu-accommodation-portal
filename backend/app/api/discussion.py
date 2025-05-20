from flask import Blueprint, request, jsonify, session
from app.models.discussion import Topic, Post, Reply, PostLike, ReplyLike
from app.extensions import db
from app.api import discussion_bp
from sqlalchemy.exc import SQLAlchemyError # type: ignore
from datetime import datetime
from functools import wraps

# 用戶身份驗證裝飾器
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "請先登入"}), 401
        
        return f(*args, **kwargs)
    return decorated

# 主題相關 API
@discussion_bp.route('/topics', methods=['GET'])
def get_topics():
    """獲取所有討論主題"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 置頂主題優先，再按更新時間排序
    query = Topic.query.order_by(Topic.is_pinned.desc(), Topic.updated_at.desc())
    topics_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = {
        'topics': [topic.to_dict() for topic in topics_pagination.items],
        'total': topics_pagination.total,
        'pages': topics_pagination.pages,
        'current_page': page
    }
    
    return jsonify(result)


@discussion_bp.route('/topics/<int:topic_id>', methods=['GET'])
def get_topic(topic_id):
    """獲取特定主題詳情"""
    topic = Topic.query.get_or_404(topic_id)
    
    # 增加瀏覽次數
    topic.view_count += 1
    db.session.commit()
    
    return jsonify(topic.to_dict())


@discussion_bp.route('/topics', methods=['POST'])
@login_required
def create_topic():
    """創建新主題"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    if not data.get('title'):
        return jsonify({'error': '主題標題不能為空'}), 400
    
    try:
        topic = Topic(
            title=data.get('title'),
            description=data.get('description', ''),
            creator_id=user_id
        )
        
        db.session.add(topic)
        db.session.commit()
        
        return jsonify(topic.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'創建主題失敗: {str(e)}'}), 500


@discussion_bp.route('/topics/<int:topic_id>', methods=['PUT'])
@login_required
def update_topic(topic_id):
    """更新主題資訊"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    topic = Topic.query.get_or_404(topic_id)
    
    # 只有創建者可以更新主題
    if topic.creator_id != user_id:
        return jsonify({'error': '您沒有權限更新此主題'}), 403
    
    try:
        if 'title' in data:
            topic.title = data['title']
        if 'description' in data:
            topic.description = data['description']
            
        db.session.commit()
        return jsonify(topic.to_dict())
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'更新主題失敗: {str(e)}'}), 500


@discussion_bp.route('/topics/<int:topic_id>', methods=['DELETE'])
@login_required
def delete_topic(topic_id):
    """刪除主題 (僅限創建者或管理員)"""
    user_id = session.get('user_id')
    
    topic = Topic.query.get_or_404(topic_id)
    
    # 只有創建者或管理員可以刪除主題
    if topic.creator_id != user_id and not session.get('is_admin', False):
        return jsonify({'error': '您沒有權限刪除此主題'}), 403
    
    try:
        db.session.delete(topic)
        db.session.commit()
        return jsonify({'message': '主題已成功刪除'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'刪除主題失敗: {str(e)}'}), 500


# 文章相關 API

@discussion_bp.route('/topics/<int:topic_id>/posts', methods=['GET'])
def get_posts(topic_id):
    """獲取特定主題下的所有文章"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 確認主題存在
    topic = Topic.query.get_or_404(topic_id)
    
    # 置頂文章優先，再按創建時間排序
    query = Post.query.filter_by(topic_id=topic_id).order_by(Post.is_pinned.desc(), Post.created_at.asc())
    posts_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = {
        'topic': topic.to_dict(),
        'posts': [post.to_dict() for post in posts_pagination.items],
        'total': posts_pagination.total,
        'pages': posts_pagination.pages,
        'current_page': page
    }
    
    return jsonify(result)


@discussion_bp.route('/topics/<int:topic_id>/posts', methods=['POST'])
@login_required
def create_post(topic_id):
    """在特定主題下發表文章"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    # 確認主題存在
    topic = Topic.query.get_or_404(topic_id)
    
    if not data.get('content'):
        return jsonify({'error': '文章內容不能為空'}), 400
    
    try:
        post = Post(
            topic_id=topic_id,
            author_id=user_id,
            content=data.get('content')
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify(post.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'發表文章失敗: {str(e)}'}), 500


@discussion_bp.route('/posts/<int:post_id>', methods=['PUT'])
@login_required
def update_post(post_id):
    """更新文章內容"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    post = Post.query.get_or_404(post_id)
    
    # 只有作者可以更新文章
    if post.author_id != user_id:
        return jsonify({'error': '您沒有權限更新此文章'}), 403
    
    if not data.get('content'):
        return jsonify({'error': '文章內容不能為空'}), 400
    
    try:
        post.content = data.get('content')
        db.session.commit()
        return jsonify(post.to_dict())
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'更新文章失敗: {str(e)}'}), 500


@discussion_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """刪除文章 (僅限作者或管理員)"""
    user_id = session.get('user_id')
    
    post = Post.query.get_or_404(post_id)
    
    # 只有作者或管理員可以刪除文章
    if post.author_id != user_id and not session.get('is_admin', False):
        return jsonify({'error': '您沒有權限刪除此文章'}), 403
    
    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': '文章已成功刪除'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'刪除文章失敗: {str(e)}'}), 500


# 回覆相關 API

@discussion_bp.route('/posts/<int:post_id>/replies', methods=['GET'])
def get_replies(post_id):
    """獲取特定文章的所有回覆"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # 確認文章存在
    post = Post.query.get_or_404(post_id)
    
    query = Reply.query.filter_by(post_id=post_id).order_by(Reply.created_at.asc())
    replies_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = {
        'post': post.to_dict(),
        'replies': [reply.to_dict() for reply in replies_pagination.items],
        'total': replies_pagination.total,
        'pages': replies_pagination.pages,
        'current_page': page
    }
    
    return jsonify(result)


@discussion_bp.route('/posts/<int:post_id>/replies', methods=['POST'])
@login_required
def create_reply(post_id):
    """對特定文章發表回覆"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    # 確認文章存在
    post = Post.query.get_or_404(post_id)
    
    if not data.get('content'):
        return jsonify({'error': '回覆內容不能為空'}), 400
    
    try:
        reply = Reply(
            post_id=post_id,
            author_id=user_id,
            content=data.get('content')
        )
        
        db.session.add(reply)
        db.session.commit()
        
        return jsonify(reply.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'發表回覆失敗: {str(e)}'}), 500


@discussion_bp.route('/replies/<int:reply_id>', methods=['PUT'])
@login_required
def update_reply(reply_id):
    """更新回覆內容"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    reply = Reply.query.get_or_404(reply_id)
    
    # 只有作者可以更新回覆
    if reply.author_id != user_id:
        return jsonify({'error': '您沒有權限更新此回覆'}), 403
    
    if not data.get('content'):
        return jsonify({'error': '回覆內容不能為空'}), 400
    
    try:
        reply.content = data.get('content')
        db.session.commit()
        return jsonify(reply.to_dict())
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'更新回覆失敗: {str(e)}'}), 500


@discussion_bp.route('/replies/<int:reply_id>', methods=['DELETE'])
@login_required
def delete_reply(reply_id):
    """刪除回覆 (僅限作者或管理員)"""
    user_id = session.get('user_id')
    
    reply = Reply.query.get_or_404(reply_id)
    
    # 只有作者或管理員可以刪除回覆
    if reply.author_id != user_id and not session.get('is_admin', False):
        return jsonify({'error': '您沒有權限刪除此回覆'}), 403
    
    try:
        db.session.delete(reply)
        db.session.commit()
        return jsonify({'message': '回覆已成功刪除'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'刪除回覆失敗: {str(e)}'}), 500


# 讚相關 API

@discussion_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """對文章按讚/取消讚"""
    user_id = session.get('user_id')
    
    # 確認文章存在
    post = Post.query.get_or_404(post_id)
    
    # 檢查是否已按讚
    existing_like = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
    
    try:
        if existing_like:
            # 取消讚
            db.session.delete(existing_like)
            message = "已取消對文章的讚"
        else:
            # 按讚
            like = PostLike(post_id=post_id, user_id=user_id)
            db.session.add(like)
            message = "已成功對文章按讚"
            
        db.session.commit()
        
        return jsonify({
            'message': message, 
            'likes': [like.user_id for like in post.likes.all()],
            'like_count': post.likes.count()
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'操作失敗: {str(e)}'}), 500


@discussion_bp.route('/replies/<int:reply_id>/like', methods=['POST'])
@login_required
def like_reply(reply_id):
    """對回覆按讚/取消讚"""
    user_id = session.get('user_id')
    
    # 確認回覆存在
    reply = Reply.query.get_or_404(reply_id)
    
    # 檢查是否已按讚
    existing_like = ReplyLike.query.filter_by(reply_id=reply_id, user_id=user_id).first()
    
    try:
        if existing_like:
            # 取消讚
            db.session.delete(existing_like)
            message = "已取消對回覆的讚"
        else:
            # 按讚
            like = ReplyLike(reply_id=reply_id, user_id=user_id)
            db.session.add(like)
            message = "已成功對回覆按讚"
            
        db.session.commit()
        
        return jsonify({
            'message': message, 
            'likes': [like.user_id for like in reply.likes.all()],
            'like_count': reply.likes.count()
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'操作失敗: {str(e)}'}), 500


# 管理員 API

@discussion_bp.route('/topics/<int:topic_id>/pin', methods=['POST'])
@login_required
def pin_topic(topic_id):
    """置頂/取消置頂主題 (僅限管理員)"""
    if not session.get('is_admin', False):
        return jsonify({'error': '您沒有管理員權限'}), 403
    
    topic = Topic.query.get_or_404(topic_id)
    
    try:
        topic.is_pinned = not topic.is_pinned
        db.session.commit()
        
        status = "置頂" if topic.is_pinned else "取消置頂"
        return jsonify({'message': f'已{status}主題', 'is_pinned': topic.is_pinned})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'操作失敗: {str(e)}'}), 500


@discussion_bp.route('/posts/<int:post_id>/pin', methods=['POST'])
@login_required
def pin_post(post_id):
    """置頂/取消置頂文章 (僅限管理員)"""
    if not session.get('is_admin', False):
        return jsonify({'error': '您沒有管理員權限'}), 403
    
    post = Post.query.get_or_404(post_id)
    
    try:
        post.is_pinned = not post.is_pinned
        db.session.commit()
        
        status = "置頂" if post.is_pinned else "取消置頂"
        return jsonify({'message': f'已{status}文章', 'is_pinned': post.is_pinned})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'操作失敗: {str(e)}'}), 500