from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.extensions import db
from app.models.user import User
from app.models.organization import Organization
from app.services.i18n_service import t

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    lang = session.get('lang', 'en')
    demo_mode = current_app.config.get('DEMO_MODE', True)

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Account is disabled. Please contact an administrator.", "danger")
                return redirect(url_for('auth.login'))

            session.clear()
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['username'] = user.username
            session['lang'] = lang

            flash(f"Welcome back, {user.username}!", "success")

            # Route by role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'ngo_staff':
                return redirect(url_for('org.dashboard'))
            elif user.role == 'employer':
                return redirect(url_for('employer.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash("Invalid username/email or password.", "danger")

    return render_template('auth/login.html', lang=lang, demo_mode=demo_mode)

@auth_bp.route('/logout')
def logout():
    lang = session.get('lang', 'en')
    session.clear()
    session['lang'] = lang
    flash("You have been signed out safely.", "info")
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    lang = session.get('lang', 'en')
    orgs = Organization.query.all()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'seeker')
        org_id = request.form.get('organization_id', type=int)

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('auth.register'))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("A user with this username or email already exists.", "danger")
            return redirect(url_for('auth.register'))

        # Only 'seeker', 'ngo_staff', 'employer' allowed from public registration
        if role not in ('seeker', 'ngo_staff', 'employer'):
            role = 'seeker'

        user = User(
            username=username,
            email=email,
            role=role,
            organization_id=org_id if role in ('ngo_staff', 'employer') else None,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', lang=lang, organizations=orgs)

# =========================================================================
# 1-CLICK DEMO LOGIN HELPERS (Enabled only when DEMO_MODE is true)
# =========================================================================
@auth_bp.route('/demo-login/<role>')
def demo_login(role):
    demo_mode = current_app.config.get('DEMO_MODE', True)
    if not demo_mode:
        flash("Demo logins are disabled in production mode.", "danger")
        return redirect(url_for('auth.login'))

    role_map = {
        'admin': 'admin@udaan.demo',
        'ngo': 'karuna.staff@udaan.demo',
        'employer': 'coastal.hr@udaan.demo',
        'seeker': 'seeker@udaan.demo'
    }

    target_email = role_map.get(role)
    if not target_email:
        flash("Invalid demo role selected.", "danger")
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=target_email).first()
    if not user:
        # Re-seed demo scenario if missing
        from scripts.seed_demo import seed_database
        seed_database()
        user = User.query.filter_by(email=target_email).first()

    if user:
        session.clear()
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['username'] = user.username
        flash(f"Signed in as Demo User: {user.username} ({user.role.upper()}).", "success")

        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'ngo_staff':
            return redirect(url_for('org.dashboard'))
        elif user.role == 'employer':
            return redirect(url_for('employer.dashboard'))
        else:
            return redirect(url_for('intake.intake_form'))

    flash("Demo account could not be initialized.", "danger")
    return redirect(url_for('auth.login'))

@auth_bp.route('/bootstrap-admin', methods=['POST'])
def bootstrap_admin():
    """Secure bootstrap mechanism for creating first admin via secret token."""
    secret = request.form.get('setup_secret')
    configured_secret = current_app.config.get('ADMIN_SETUP_SECRET', 'UdaanAdminBootstrap2026!')

    if not secret or secret != configured_secret:
        flash("Invalid administrator bootstrap secret.", "danger")
        return redirect(url_for('auth.login'))

    username = request.form.get('username', 'system_admin').strip()
    email = request.form.get('email', 'admin@udaan.org').strip()
    password = request.form.get('password')

    if not password or len(password) < 8:
        flash("Password must be at least 8 characters long.", "danger")
        return redirect(url_for('auth.login'))

    existing = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing:
        flash("User already exists.", "warning")
        return redirect(url_for('auth.login'))

    admin = User(username=username, email=email, role='admin', is_active=True)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    flash("Administrator account successfully bootstrapped! You can now log in.", "success")
    return redirect(url_for('auth.login'))
