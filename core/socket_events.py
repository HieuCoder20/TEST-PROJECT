from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from core import socketio, db
from core.models import Message, Notification

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        print(f'User {current_user.username} connected and joined room user_{current_user.id}')

@socketio.on('send_message')
def handle_send_message(data):
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    
    if not recipient_id or not content:
        return

    # Lưu tin nhắn vào DB
    new_msg = Message(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        content=content
    )
    db.session.add(new_msg)
    
    # Tạo thông báo cho người nhận
    new_notif = Notification(
        user_id=recipient_id,
        content=f'Bạn có tin nhắn mới từ {current_user.username}',
        n_type='message',
        related_id=current_user.id
    )
    db.session.add(new_notif)
    db.session.commit()
    
    # Gửi real-time qua SocketIO
    emit('receive_message', {
        'sender_id': current_user.id,
        'sender_username': current_user.username,
        'content': content,
        'timestamp': new_msg.timestamp.strftime('%H:%M')
    }, room=f'user_{recipient_id}')
    
    # Gửi lại cho người gửi để hiển thị (hoặc client tự xử lý)
    emit('message_sent', {
        'content': content,
        'timestamp': new_msg.timestamp.strftime('%H:%M')
    })

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')

