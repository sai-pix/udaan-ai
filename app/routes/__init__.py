from app.routes.main import main_bp
from app.routes.intake import intake_bp
from app.routes.pathway import pathway_bp
from app.routes.referral import referral_bp
from app.routes.org_dashboard import org_bp
from app.routes.employer import employer_bp
from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.api import api_bp

__all__ = [
    'main_bp',
    'intake_bp',
    'pathway_bp',
    'referral_bp',
    'org_bp',
    'employer_bp',
    'admin_bp',
    'auth_bp',
    'api_bp'
]
