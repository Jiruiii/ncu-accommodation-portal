from app import create_app, socketio
import os

app = create_app()

if __name__ == '__main__':
    # 生產模式：關閉 debug
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    socketio.run(app, host='0.0.0.0', port=5000, debug=debug_mode)