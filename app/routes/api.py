import os
from flask import Blueprint, jsonify, request
from sqlalchemy import func
from app.extensions import db
from app.models.resource import Resource
from app.models.referral import ReferralRequest
from app.models.seeker_profile import SupportSeekerProfile
from app.models.pathway import PathwayStep

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health')
def health_check():
    db_ok = True
    try:
        db.session.execute(db.text('SELECT 1'))
    except Exception:
        db_ok = False

    gemini_key = os.environ.get('GEMINI_API_KEY')
    return jsonify({
        'status': 'healthy' if db_ok else 'unhealthy',
        'service': 'Udaan AI — Barrier-Aware Livelihood Pathways',
        'version': '1.0.0',
        'database_connected': db_ok,
        'gemini_configured': bool(gemini_key),
        'demo_mode': os.environ.get('DEMO_MODE', 'true').lower() in ('true', '1', 'yes')
    }), 200 if db_ok else 503

@api_bp.route('/step/<int:step_id>/toggle', methods=['POST'])
def toggle_step(step_id):
    step = db.session.get(PathwayStep, step_id)
    if not step:
        return jsonify({'error': 'Step not found'}), 404

    data = request.get_json() or {}
    new_status = data.get('status')
    if new_status in ('pending', 'in_progress', 'completed', 'skipped'):
        step.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'step_id': step.id, 'status': step.status})

    return jsonify({'error': 'Invalid status'}), 400

@api_bp.route('/impact-stats')
def impact_stats():
    """Aggregated, non-PII impact statistics using fast SQL GROUP BY."""
    categories = ['shelter', 'food', 'training', 'employment', 'documentation', 'rehabilitation']
    grouped_cats = dict(db.session.query(Resource.category, func.count(Resource.id)).group_by(Resource.category).all())
    cat_distribution = {c: grouped_cats.get(c, 0) for c in categories}
    
    status_list = ['submitted', 'under_review', 'accepted', 'contacted', 'appointment_scheduled', 'completed', 'declined']
    grouped_statuses = dict(db.session.query(ReferralRequest.status, func.count(ReferralRequest.id)).group_by(ReferralRequest.status).all())
    referral_distribution = {s: grouped_statuses.get(s, 0) for s in status_list}

    return jsonify({
        'total_profiles': SupportSeekerProfile.query.count(),
        'total_referrals': ReferralRequest.query.count(),
        'completed_referrals': ReferralRequest.query.filter_by(status='completed').count(),
        'category_distribution': cat_distribution,
        'referral_distribution': referral_distribution
    })
