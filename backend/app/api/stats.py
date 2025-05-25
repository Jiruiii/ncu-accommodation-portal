from flask import Blueprint, jsonify
from app.models import User, Accommodation
from app.api import api_bp 

statistics_bp = Blueprint('statistics', __name__, url_prefix='/api/statistics')

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        # 獲取用戶總數 (排除管理員和超級管理員)
        user_count = User.query.count()
        
        # 獲取房源總數
        property_count = Accommodation.query.count()
        
        return jsonify({
            'success': True,
            'data': {
                'user_count': user_count,
                'property_count': property_count,
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'獲取統計數據失敗: {str(e)}'
        }), 500