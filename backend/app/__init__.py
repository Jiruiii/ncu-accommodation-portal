from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS # type: ignore
from flask_session import Session # type: ignore
from flask_socketio import SocketIO
from flask_migrate import Migrate # type: ignore
from datetime import timedelta
from config import config
from app.extensions import db, migrate, jwt
from dotenv import load_dotenv
import os 

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_name='default'):
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
    socketio.init_app(app)
    
    # 註冊藍圖
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 確保上傳目錄存在
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # 確保 profiles 子目錄存在
    profiles_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles')
    if not os.path.exists(profiles_dir):
        os.makedirs(profiles_dir)
    
    # 修正靜態檔案路由
    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        # 添加調試信息
        print(f"請求訪問檔案: {filename}")
        print(f"檔案完整路徑: {os.path.join(app.config['UPLOAD_FOLDER'], filename)}")
        
        # 檢查檔案是否存在
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            print(f"檔案存在，大小: {os.path.getsize(file_path)} bytes")
        else:
            print(f"檔案不存在!")
        
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    return app