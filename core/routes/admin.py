from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from core.models import User, Post, Claim, db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def ensure_admin():
    if not current_user.is_admin:
        abort(403)

@admin_bp.route('/')
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_posts': Post.query.count(),
        'lost_count': Post.query.filter_by(item_type='lost').count(),
        'found_count': Post.query.filter_by(item_type='found').count()
    }
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users)

@admin_bp.route('/users')
def user_management():
    # Phân trang 20 user/trang
    from flask import request
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)

