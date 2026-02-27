from gevent import monkey
monkey.patch_all()

import os
from dotenv import load_dotenv
load_dotenv()

from core import create_app, socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Chế độ debug chỉ bật khi chạy local
    is_dev = os.getenv("FLASK_ENV") == "development"
    socketio.run(app, host="0.0.0.0", port=port, debug=is_dev)
