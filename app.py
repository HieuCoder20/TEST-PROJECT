from gevent import monkey
monkey.patch_all() # Phải là dòng code thực thi đầu tiên

import os
from dotenv import load_dotenv
load_dotenv()

# Giờ mới import các thành phần của app
from core import create_app, socketio

app = create_app()

if __name__ == "__main__":
    # Lưu ý: socketio.run chỉ dùng cho môi trường local (development)
    port = int(os.environ.get("PORT", 5000))
    is_dev = os.getenv("FLASK_ENV") == "development"
    socketio.run(app, host="0.0.0.0", port=port, debug=is_dev)
