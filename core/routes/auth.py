from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from core.models import User, db
import re

auth_bp = Blueprint('auth', __name__)

def is_password_strong(password):
    # Ít nhất 8 ký tự, có cả chữ và số
    if len(password) < 8:
        return False
    if not re.search("[a-zA-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    return True

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username hoặc Email đã tồn tại.', 'danger')
        elif password != confirm_password:
            flash('Mật khẩu nhập lại không khớp.', 'danger')
        elif not is_password_strong(password):
            flash('Mật khẩu phải có ít nhất 8 ký tự, bao gồm cả chữ và số.', 'danger')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
            
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.is_locked:
                flash('Tài khoản của bạn đã bị khóa.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
