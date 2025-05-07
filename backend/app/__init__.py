from flask import Flask
from flask_cors import CORS # type: ignore

from config import config
from app.extensions import db, migrate, jwt
from dotenv import load_dotenv

def create_app(config_name='default'):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化擴展
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 註冊藍圖
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 建立上傳資料夾
    import os
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    return app