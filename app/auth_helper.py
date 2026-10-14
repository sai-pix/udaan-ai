from functools import wraps
from flask import session, redirect, url_for, flash, request, abort
from app.models.user import User

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        user = get_current_user()
        if not user or not user.is_active:
            session.clear()
            flash("Your account is inactive or not found.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please sign in to access this portal.", "warning")
                return redirect(url_for('auth.login', next=request.url))
            user = get_current_user()
            if not user or not user.is_active:
                session.clear()
                flash("Your account is inactive.", "danger")
                return redirect(url_for('auth.login'))
            if user.role not in roles:
                flash("Access denied: You do not have permissions for this section.", "danger")
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
