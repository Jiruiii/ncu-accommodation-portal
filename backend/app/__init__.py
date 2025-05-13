from flask import Flask
from flask_cors import CORS # type: ignore
from flask_session import Session # type: ignore
from datetime import timedelta
from config import config
from app.extensions import db, migrate, jwt
from dotenv import load_dotenv
import os 

def create_app(config_name='default'):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Session 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key-here'  # 添加預設值
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(app.instance_path), 'flask_session')
    
    # 確保 Cookie 設置正確
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # 開發環境設為 False，生產環境設為 True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # 初始化 Session
    Session(app)  
    
    # 初始化 CORS
    CORS(app, 
        supports_credentials=True, 
        resources={r"/*": {
            "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],  
            "methods": ["GET", "POST", "PUT", "DELETE","OPTIONS"],  
            "allow_headers": ["Content-Type", "Authorization", "Cookie"],  # 添加 Cookie
            "expose_headers": ["Content-Length", "X-JSON"],  
        }}
    )
    
    
    # 診斷路由
    @app.route('/debug-session', methods=['GET'])
    def debug_session():
        from flask import session, jsonify
        return jsonify({
            'session_data': dict(session),
            'has_user_id': 'user_id' in session,
            'user_id': session.get('user_id')
        })
    
    # 初始化其他擴展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)  # 即使不使用 JWT，保留此行也沒有害處
    
    # 註冊藍圖
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 建立上傳資料夾
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    return app