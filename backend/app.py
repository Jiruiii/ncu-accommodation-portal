from app import create_app, socketio
import threading

app = create_app()

def run_socketio():
    socketio.run(app, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    # thread = threading.Thread(target=run_socketio)
    # thread.daemon = True  # 將線程設為守護線程，主程序結束時自動終止
    # thread.start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
