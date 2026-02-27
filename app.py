import eventlet
eventlet.monkey_patch(all=True)

import os
from dotenv import load_dotenv
load_dotenv()

from core import create_app, socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=(os.getenv("FLASK_ENV") == "development"))
