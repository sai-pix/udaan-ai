from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.extensions import db
from app.models.organization import Organization
from app.models.resource import Resource
from app.models.opportunity import Opportunity
from app.models.referral import ReferralRequest
from app.models.seeker_profile import SupportSeekerProfile
from app.models.audit import AuditEvent
from app.models.followup import FollowUpRecord
from app.services.verification_service import VerificationService
from app.auth_helper import login_required, roles_required, get_current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
@roles_required('admin')
def dashboard():
    lang = session.get('lang', 'en')
    current_user = get_current_user()

    # Aggregate impact metrics (privacy-preserving, no individual PII)
    total_profiles = SupportSeekerProfile.query.count()
    total_referrals = ReferralRequest.query.count()
    completed_referrals = ReferralRequest.query.filter_by(status='completed').count()
    active_referrals = ReferralRequest.query.filter(ReferralRequest.status.in_(['submitted', 'under_review', 'accepted', 'contacted', 'appointment_scheduled'])).count()
    
    total_orgs = Organization.query.count()
    verified_orgs = Organization.query.filter_by(verification_status='verified').count()
    pending_orgs = Organization.query.filter_by(verification_status='pending_review').count()

    total_resources = Resource.query.count()
    verified_resources = Resource.query.filter_by(verified=True).count()

    # Category counts for Chart.js
    categories = ['shelter', 'food', 'training', 'employment', 'documentation', 'rehabilitation']
    cat_counts = {}
    for c in categories:
        cat_counts[c] = Resource.query.filter_by(category=c).count()

    # Referral statuses for Chart.js
    status_list = ['submitted', 'under_review', 'accepted', 'contacted', 'appointment_scheduled', 'completed', 'declined']
    referral_status_counts = {}
    for s in status_list:
        referral_status_counts[s] = ReferralRequest.query.filter_by(status=s).count()

    recent_audits = AuditEvent.query.order_by(AuditEvent.timestamp.desc()).limit(15).all()

    return render_template(
        'admin/dashboard.html',
        lang=lang,
        current_user=current_user,
        total_profiles=total_profiles,
        total_referrals=total_referrals,
        completed_referrals=completed_referrals,
        active_referrals=active_referrals,
        total_orgs=total_orgs,
        verified_orgs=verified_orgs,
        pending_orgs=pending_orgs,
        total_resources=total_resources,
        verified_resources=verified_resources,
        cat_counts=cat_counts,
        referral_status_counts=referral_status_counts,
        recent_audits=recent_audits
    )

@admin_bp.route('/admin/organizations')
@login_required
@roles_required('admin')
def organizations():
    lang = session.get('lang', 'en')
    current_user = get_current_user()
    orgs = Organization.query.order_by(Organization.created_at.desc()).all()
    return render_template('admin/organizations.html', lang=lang, current_user=current_user, organizations=orgs)

@admin_bp.route('/admin/organization/<int:org_id>/verify', methods=['POST'])
@login_required
@roles_required('admin')
def verify_organization(org_id):
    current_user = get_current_user()
    status = request.form.get('status', 'verified')
    source = request.form.get('verification_source', 'Admin Manual Review')
    notes = request.form.get('internal_notes')

    VerificationService.verify_organization(org_id, status, source, current_user, notes)
    flash(f"Organization status updated to {status}.", "success")
    return redirect(url_for('admin.organizations'))

@admin_bp.route('/admin/resources')
@login_required
@roles_required('admin')
def resources():
    lang = session.get('lang', 'en')
    current_user = get_current_user()
    all_resources = Resource.query.order_by(Resource.category.asc(), Resource.name.asc()).all()
    return render_template('admin/resources.html', lang=lang, current_user=current_user, resources=all_resources)

@admin_bp.route('/admin/resource/<int:res_id>/toggle-verify', methods=['POST'])
@login_required
@roles_required('admin')
def toggle_resource_verify(res_id):
    current_user = get_current_user()
    res = Resource.query.get_or_404(res_id)
    VerificationService.verify_resource(res_id, not res.verified, current_user)
    flash(f"Resource {res.name} verification status set to {not res.verified}.", "info")
    return redirect(url_for('admin.resources'))

@admin_bp.route('/admin/audit-logs')
@login_required
@roles_required('admin')
def audit_logs():
    lang = session.get('lang', 'en')
    current_user = get_current_user()
    audits = AuditEvent.query.order_by(AuditEvent.timestamp.desc()).limit(100).all()
    return render_template('admin/audit_logs.html', lang=lang, current_user=current_user, audits=audits)
