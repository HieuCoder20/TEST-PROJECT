import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO

# Khởi tạo các Extension
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# QUAN TRỌNG: async_mode PHẢI LÀ 'gevent'
socketio = SocketIO(cors_allowed_origins="*", async_mode='gevent')

def create_app():
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    # Cấu hình Secret Key
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # Cấu hình Database cho Render
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///lost_found.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Khởi tạo Extension với app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Register Blueprints
    from core.routes.auth import auth_bp
    from core.routes.main import main_bp
    from core.routes.chat import chat_bp
    from core.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        from core import socket_events

    return app
