from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from core.models import Post, db
from core.ai_guard import AIGuardrail
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(Post.status != 'returned')\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=10)
    
    return render_template('main/index.html', posts=posts)

@main_bp.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        item_type = request.form.get('item_type')
        category = request.form.get('category')
        location_building = request.form.get('location_building')
        location_room = request.form.get('location_room')
        lost_found_time_str = request.form.get('lost_found_time')
        
        # 1. AI Guardrail Check
        is_duplicate, similarity = AIGuardrail.check_duplicate(description, current_user.id)
        if is_duplicate:
            flash(f'Cảnh báo: Hệ thống phát hiện bài đăng này giống {similarity*100:.1f}% với bài đăng cũ của bạn. Vui lòng không spam.', 'danger')
            return render_template('main/create_post.html')

        # 2. Xử lý thời gian
        try:
            lost_found_time = datetime.strptime(lost_found_time_str, '%Y-%m-%dT%H:%M')
        except:
            lost_found_time = datetime.utcnow()
        
        # 3. Tạo post mới
        new_post = Post(
            title=title,
            description=description,
            item_type=item_type,
            category=category,
            location_building=location_building,
            location_room=location_room,
            lost_found_time=lost_found_time,
            user_id=current_user.id,
            image_urls=[], # Cloudinary sẽ tích hợp sau
            contact_info={
                'email': current_user.email if request.form.get('show_email') else None,
                'phone': current_user.phone if request.form.get('show_phone') else None
            }
        )
        
        db.session.add(new_post)
        db.session.commit()
        flash('Đăng tin thành công!', 'success')
        return redirect(url_for('main.index'))

    return render_template('main/create_post.html')

@main_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('main/post_detail.html', post=post)

@main_bp.route('/post/<int:post_id>/claim', methods=['POST'])
@login_required
def claim_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id == current_user.id:
        flash('Bạn không thể claim bài đăng của chính mình.', 'danger')
        return redirect(url_for('main.post_detail', post_id=post_id))
    
    verification_info = request.form.get('verification_info')
    from core.models import Claim, Notification
    
    new_claim = Claim(
        post_id=post.id,
        requester_id=current_user.id,
        verification_info=verification_info
    )
    
    # Tạo thông báo cho người đăng
    new_notif = Notification(
        user_id=post.user_id,
        content=f'{current_user.username} đã gửi yêu cầu xác minh đồ cho bài đăng: {post.title}',
        n_type='claim',
        related_id=post.id
    )
    
    db.session.add(new_claim)
    db.session.add(new_notif)
    db.session.commit()
    
    flash('Yêu cầu xác minh đã được gửi thành công. Vui lòng chờ phản hồi từ người đăng.', 'success')
    return redirect(url_for('main.post_detail', post_id=post_id))

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    # Tạm thời sử dụng filter cơ bản, sẽ nâng cấp lên Fuzzy Search sau
    posts = Post.query.filter(
        (Post.title.contains(query)) | (Post.description.contains(query))
    ).filter(Post.status != 'returned').all()
    
    return render_template('main/search_results.html', posts=posts, query=query)
