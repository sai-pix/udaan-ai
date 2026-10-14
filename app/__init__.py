import os
from flask import Flask, render_template, session, request
from app.config import Config
from app.extensions import db
from app.auth_helper import get_current_user
from app.services.i18n_service import t

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes import (
        main_bp,
        intake_bp,
        pathway_bp,
        referral_bp,
        org_bp,
        employer_bp,
        admin_bp,
        auth_bp,
        api_bp
    )

    app.register_blueprint(main_bp)
    app.register_blueprint(intake_bp)
    app.register_blueprint(pathway_bp)
    app.register_blueprint(referral_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(employer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # Context processor for Jinja2 templates
    @app.context_processor
    def inject_global_template_vars():
        current_lang = session.get('lang', app.config.get('DEFAULT_LANGUAGE', 'en'))
        return {
            't': lambda key, default=None: t(key, lang=current_lang, default=default),
            'current_lang': current_lang,
            'demo_mode': app.config.get('DEMO_MODE', True),
            'current_user': get_current_user()
        }

    # Friendly error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
