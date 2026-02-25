from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from core.models import Message, User

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/messages')
@login_required
def messages():
    # Lấy danh sách các cuộc hội thoại (tạm thời lấy tất cả tin nhắn liên quan)
    # Trong thực tế sẽ cần query phức tạp hơn để lấy danh sách user đã chat
    recent_messages = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.timestamp.desc()).limit(50).all()
    
    return render_template('chat/messages.html', messages=recent_messages)

@chat_bp.route('/chat/<int:user_id>')
@login_required
def start_chat(user_id):
    recipient = User.query.get_or_404(user_id)
    if recipient.id == current_user.id:
        flash("Bạn không thể chat với chính mình!", "warning")
        return redirect(url_for('main.index'))
    
    # Ở đây có thể lấy lịch sử chat giữa 2 người
    chat_history = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient.id)) |
        ((Message.sender_id == recipient.id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    
    return render_template('chat/messages.html', recipient=recipient, chat_history=chat_history)
