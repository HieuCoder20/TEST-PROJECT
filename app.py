import os
from dotenv import load_dotenv
load_dotenv()

from core import create_app, socketio

app = create_app()

if __name__ == "__main__":
    # Chỉ dùng monkey patch khi chạy local bằng lệnh: python app.py
    from gevent import monkey
    monkey.patch_all()
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
