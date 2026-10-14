from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from app.extensions import db
from app.models.organization import Organization
from app.models.referral import ReferralRequest
from app.services.referral_service import ReferralService
from app.auth_helper import login_required, roles_required, get_current_user

org_bp = Blueprint('org', __name__)

@org_bp.route('/org/dashboard')
@login_required
@roles_required('ngo_staff', 'admin')
def dashboard():
    lang = session.get('lang', 'en')
    current_user = get_current_user()

    # Determine which organization to show
    if current_user.role == 'admin':
        org_id = request.args.get('org_id', type=int) or current_user.organization_id or 1
        org = Organization.query.get_or_404(org_id)
    else:
        if not current_user.organization_id:
            flash("Your staff account is not assigned to any organization.", "warning")
            return redirect(url_for('main.index'))
        org = current_user.organization

    status_filter = request.args.get('status')
    referral_query = ReferralRequest.query.filter_by(organization_id=org.id)
    if status_filter:
        referral_query = referral_query.filter_by(status=status_filter)

    referrals = referral_query.order_by(ReferralRequest.created_at.desc()).all()

    # Counts by status
    all_refs = ReferralRequest.query.filter_by(organization_id=org.id).all()
    counts = {
        'total': len(all_refs),
        'submitted': sum(1 for r in all_refs if r.status == 'submitted'),
        'under_review': sum(1 for r in all_refs if r.status == 'under_review'),
        'accepted': sum(1 for r in all_refs if r.status == 'accepted'),
        'contacted': sum(1 for r in all_refs if r.status == 'contacted'),
        'scheduled': sum(1 for r in all_refs if r.status == 'appointment_scheduled'),
        'completed': sum(1 for r in all_refs if r.status == 'completed'),
        'declined': sum(1 for r in all_refs if r.status == 'declined')
    }

    return render_template(
        'org/dashboard.html',
        lang=lang,
        current_user=current_user,
        organization=org,
        referrals=referrals,
        counts=counts,
        current_status_filter=status_filter
    )

@org_bp.route('/org/referral/<int:referral_id>', methods=['GET', 'POST'])
@login_required
@roles_required('ngo_staff', 'admin')
def referral_detail(referral_id):
    lang = session.get('lang', 'en')
    current_user = get_current_user()
    referral = ReferralRequest.query.get_or_404(referral_id)

    # STRICT ISOLATION CHECK
    if current_user.role == 'ngo_staff' and referral.organization_id != current_user.organization_id:
        abort(403) # Forbidden

    if request.method == 'POST':
        new_status = request.form.get('status')
        staff_notes = request.form.get('staff_notes', '').strip()
        appointment_date_str = request.form.get('appointment_date')
        outcome_summary = request.form.get('outcome_summary', '').strip()

        appointment_date = None
        if appointment_date_str:
            try:
                appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass

        try:
            ReferralService.update_status(
                referral_id=referral.id,
                new_status=new_status,
                current_user=current_user,
                staff_notes=staff_notes,
                appointment_date=appointment_date,
                outcome_summary=outcome_summary,
                ip_address=request.remote_addr
            )
            flash(f"Referral {referral.reference_number} updated to '{new_status}'.", "success")
            return redirect(url_for('org.referral_detail', referral_id=referral.id))
        except Exception as e:
            flash(f"Error updating referral: {str(e)}", "danger")

    return render_template(
        'org/referral_detail.html',
        lang=lang,
        current_user=current_user,
        referral=referral,
        organization=referral.organization,
        allowed_statuses=ReferralService.ALLOWED_STATUSES
    )
