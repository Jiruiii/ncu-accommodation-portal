from app import create_app, socketio
import threading

app = create_app()

def run_socketio():
    print("start up WebSocket...")
    socketio.run(app, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    # 啟動 WebSocket 於獨立執行緒
    thread = threading.Thread(target=run_socketio)
    thread.start()
    
    app.run(debug=True , host='0.0.0.0', port=5000)
    # socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)