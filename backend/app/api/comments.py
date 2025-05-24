from flask import Blueprint, request, jsonify, session
from app.models.comments import Comment, Reply, CommentLike, ReplyLike
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError # type: ignore
from datetime import datetime
from functools import wraps
from app.api import comments_bp

# 用戶身份驗證裝飾器
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "請先登入"}), 401
        
        return f(*args, **kwargs)
    return decorated

# 評論相關 API
@comments_bp.route('/property/<int:property_id>', methods=['GET'])
def get_property_comments(property_id):
    """獲取特定房源的所有評論"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Comment.query.filter_by(property_id=property_id).order_by(Comment.created_at.desc())
    comments_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = {
        'comments': [comment.to_dict() for comment in comments_pagination.items],
        'total': comments_pagination.total,
        'pages': comments_pagination.pages,
        'current_page': page
    }
    
    return jsonify(result)

@comments_bp.route('/property/<int:property_id>', methods=['POST'])
@login_required
def create_comment(property_id):
    """對特定房源發表評論"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    if not data.get('content'):
        return jsonify({'error': '評論內容不能為空'}), 400
    
    if not data.get('rating') or not isinstance(data.get('rating'), int) or data.get('rating') < 1 or data.get('rating') > 5:
        return jsonify({'error': '評分必須為1-5的整數'}), 400
    
    try:
        comment = Comment(
            property_id=property_id,
            user_id=user_id,
            content=data.get('content'),
            rating=data.get('rating')
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify(comment.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'發表評論失敗: {str(e)}'}), 500

@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@login_required
def update_comment(comment_id):
    """更新評論內容和評分"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    comment = Comment.query.get_or_404(comment_id)
    
    # 只有作者可以更新評論
    if comment.user_id != user_id:
        return jsonify({'error': '您沒有權限更新此評論'}), 403
    
    if not data.get('content'):
        return jsonify({'error': '評論內容不能為空'}), 400
    
    if 'rating' in data and (not isinstance(data.get('rating'), int) or data.get('rating') < 1 or data.get('rating') > 5):
        return jsonify({'error': '評分必須為1-5的整數'}), 400
    
    try:
        comment.content = data.get('content', comment.content)
        if 'rating' in data:
            comment.rating = data.get('rating')
        
        db.session.commit()
        return jsonify(comment.to_dict())
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'更新評論失敗: {str(e)}'}), 500

@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """刪除評論 (僅限作者或管理員)"""
    user_id = session.get('user_id')
    
    comment = Comment.query.get_or_404(comment_id)
    
    # 只有作者或管理員可以刪除評論
    if comment.user_id != user_id and not session.get('is_admin', False):
        return jsonify({'error': '您沒有權限刪除此評論'}), 403
    
    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': '評論已成功刪除'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'刪除評論失敗: {str(e)}'}), 500

# 回覆相關 API
@comments_bp.route('/<int:comment_id>/replies', methods=['GET'])
def get_replies(comment_id):
    """獲取特定評論的所有回覆"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # 確認評論存在
    comment = Comment.query.get_or_404(comment_id)
    
    query = Reply.query.filter_by(comment_id=comment_id).order_by(Reply.created_at.asc())
    replies_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = {
        'comment': comment.to_dict(),
        'replies': [reply.to_dict() for reply in replies_pagination.items],
        'total': replies_pagination.total,
        'pages': replies_pagination.pages,
        'current_page': page
    }
    
    return jsonify(result)

@comments_bp.route('/<int:comment_id>/replies', methods=['POST'])
@login_required
def create_reply(comment_id):
    """對特定評論發表回覆"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    # 確認評論存在
    comment = Comment.query.get_or_404(comment_id)
    
    if not data.get('content'):
        return jsonify({'error': '回覆內容不能為空'}), 400
    
    try:
        reply = Reply(
            comment_id=comment_id,
            user_id=user_id,
            content=data.get('content')
        )
        
        db.session.add(reply)
        db.session.commit()
        
        return jsonify(reply.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'發表回覆失敗: {str(e)}'}), 500

@comments_bp.route('/replies/<int:reply_id>', methods=['PUT'])
@login_required
def update_reply(reply_id):
    """更新回覆內容"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    reply = Reply.query.get_or_404(reply_id)
    
    # 只有作者可以更新回覆
    if reply.user_id != user_id:
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

@comments_bp.route('/replies/<int:reply_id>', methods=['DELETE'])
@login_required
def delete_reply(reply_id):
    """刪除回覆 (僅限作者或管理員)"""
    user_id = session.get('user_id')
    
    reply = Reply.query.get_or_404(reply_id)
    
    # 只有作者或管理員可以刪除回覆
    if reply.user_id != user_id and not session.get('is_admin', False):
        return jsonify({'error': '您沒有權限刪除此回覆'}), 403
    
    try:
        db.session.delete(reply)
        db.session.commit()
        return jsonify({'message': '回覆已成功刪除'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'刪除回覆失敗: {str(e)}'}), 500

@comments_bp.route('/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    """對評論按讚/取消讚"""
    user_id = session.get('user_id')
    
    # 確認評論存在
    comment = Comment.query.get_or_404(comment_id)
    
    # 檢查是否已按讚
    existing_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=user_id).first()
    is_liked = False
    
    try:
        if existing_like:
            # 取消讚
            db.session.delete(existing_like)
            message = "已取消對評論的讚"
        else:
            # 按讚
            like = CommentLike(comment_id=comment_id, user_id=user_id)
            db.session.add(like)
            message = "已成功對評論按讚"
            is_liked = True
            
        db.session.commit()
        
        # 重新查詢以獲取最新的點讚資訊
        likes_count = CommentLike.query.filter_by(comment_id=comment_id).count()
        liked_by = [like.user_id for like in CommentLike.query.filter_by(comment_id=comment_id).all()]
        
        return jsonify({
            'message': message, 
            'likes': likes_count,
            'likedBy': liked_by,
            'isLiked': is_liked
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'操作失敗: {str(e)}'}), 500

@comments_bp.route('/replies/<int:reply_id>/like', methods=['POST'])
@login_required
def like_reply(reply_id):
    """對回覆按讚/取消讚"""
    user_id = session.get('user_id')
    
    # 確認回覆存在
    reply = Reply.query.get_or_404(reply_id)
    
    # 檢查是否已按讚
    existing_like = ReplyLike.query.filter_by(reply_id=reply_id, user_id=user_id).first()
    is_liked = False
    
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
            is_liked = True
            
        db.session.commit()
        
        # 重新查詢以獲取最新的點讚資訊
        likes_count = ReplyLike.query.filter_by(reply_id=reply_id).count()
        liked_by = [like.user_id for like in ReplyLike.query.filter_by(reply_id=reply_id).all()]
        
        return jsonify({
            'message': message, 
            'like_count': likes_count,
            'likes': liked_by,
            'isLiked': is_liked
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'操作失敗: {str(e)}'}), 500