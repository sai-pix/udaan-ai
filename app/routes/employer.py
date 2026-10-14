from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from app.extensions import db
from app.models.organization import Organization
from app.models.opportunity import Opportunity
from app.models.referral import ReferralRequest
from app.services.i18n_service import t, PILOT_CITIES
from app.auth_helper import login_required, roles_required, get_current_user

employer_bp = Blueprint('employer', __name__)

@employer_bp.route('/employer/dashboard')
@login_required
@roles_required('employer', 'admin')
def dashboard():
    lang = session.get('lang', 'en')
    current_user = get_current_user()

    if current_user.role == 'admin':
        org_id = request.args.get('org_id', type=int) or current_user.organization_id or 4
        org = db.get_or_404(Organization, org_id)
    else:
        if not current_user.organization_id:
            flash("Your employer account is not linked to an organization profile.", "warning")
            return redirect(url_for('main.index'))
        org = current_user.organization

    opportunities = Opportunity.query.filter_by(organization_id=org.id).all()
    referrals = ReferralRequest.query.filter_by(organization_id=org.id).order_by(ReferralRequest.created_at.desc()).all()

    return render_template(
        'employer/dashboard.html',
        lang=lang,
        current_user=current_user,
        organization=org,
        opportunities=opportunities,
        referrals=referrals
    )

@employer_bp.route('/employer/opportunity/new', methods=['GET', 'POST'])
@login_required
@roles_required('employer', 'admin')
def create_opportunity():
    lang = session.get('lang', 'en')
    current_user = get_current_user()

    org = current_user.organization or Organization.query.first()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        opp_type = request.form.get('opportunity_type', 'job')
        description = request.form.get('description', '').strip()
        locality = request.form.get('location_locality', '').strip()
        city = request.form.get('city', org.city)
        wage = request.form.get('wage_or_stipend', '').strip()
        hours = request.form.get('hours_type', 'full_time')
        skills_raw = request.form.get('requirements_skills', '')
        skills = [s.strip() for s in skills_raw.split(',') if s.strip()]
        education = request.form.get('requirements_education', 'No formal degree required')
        documentation = request.form.get('requirements_documentation', 'Basic identity or Aadhaar assistance acceptable')
        prerequisites = request.form.get('prerequisites', '').strip()

        if not title:
            flash("Job/Opportunity title is required.", "danger")
            return redirect(url_for('employer.create_opportunity'))

        opp = Opportunity(
            organization_id=org.id,
            title=title,
            opportunity_type=opp_type,
            description=description,
            employer_name=org.name,
            location_locality=locality,
            city=city,
            wage_or_stipend=wage,
            hours_type=hours,
            requirements_skills=skills,
            requirements_education=education,
            requirements_documentation=documentation,
            prerequisites=prerequisites,
            is_active=True,
            verification_status='pending_review' if not org.is_demo_data else 'verified',
            is_demo_data=org.is_demo_data
        )
        db.session.add(opp)
        db.session.commit()

        flash(f"Opportunity '{title}' successfully created!", "success")
        return redirect(url_for('employer.dashboard'))

    return render_template(
        'employer/opportunity_form.html',
        lang=lang,
        current_user=current_user,
        organization=org,
        pilot_cities=PILOT_CITIES,
        opportunity=None
    )

@employer_bp.route('/employer/opportunity/<int:opp_id>/toggle', methods=['POST'])
@login_required
@roles_required('employer', 'admin')
def toggle_opportunity(opp_id):
    current_user = get_current_user()
    opp = db.get_or_404(Opportunity, opp_id)

    if current_user.role == 'employer' and opp.organization_id != current_user.organization_id:
        abort(403)

    opp.is_active = not opp.is_active
    db.session.commit()
    flash(f"Opportunity status set to {'Active' if opp.is_active else 'Inactive'}.", "info")
    return redirect(url_for('employer.dashboard'))
