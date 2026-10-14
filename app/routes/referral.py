from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models.organization import Organization
from app.models.opportunity import Opportunity
from app.models.seeker_profile import SupportSeekerProfile
from app.models.referral import ReferralRequest
from app.services.referral_service import ReferralService
from app.services.i18n_service import t
from app.auth_helper import get_current_user

referral_bp = Blueprint('referral', __name__)

@referral_bp.route('/referral/create/<int:org_id>', methods=['GET', 'POST'])
def create_referral_request(org_id):
    lang = session.get('lang', 'en')
    current_user = get_current_user()

    org = Organization.query.get_or_404(org_id)
    opp_id = request.args.get('opp_id', type=int)
    opp = Opportunity.query.get(opp_id) if opp_id else None

    profile_id = session.get('profile_id')
    profile = SupportSeekerProfile.query.get(profile_id) if profile_id else None

    if request.method == 'POST':
        consent = request.form.get('referral_consent')
        if not consent:
            flash("Explicit consent is required to share your information with the organization.", "danger")
            return redirect(url_for('referral.create_referral_request', org_id=org.id, opp_id=opp_id))

        alias_name = request.form.get('alias_name', '').strip() or (profile.alias_name if profile else 'Community Member')
        phone = request.form.get('contact_phone', '').strip() or (profile.contact_phone if profile else None)

        if not profile:
            # Create a lightweight profile if none exists in session
            profile = SupportSeekerProfile(
                alias_name=alias_name,
                contact_phone=phone,
                preferred_language=lang,
                city=org.city,
                consent_given=True
            )
            db.session.add(profile)
            db.session.commit()
            session['profile_id'] = profile.id

        referral = ReferralService.create_referral(
            profile_id=profile.id,
            organization_id=org.id,
            opportunity_id=opp.id if opp else None,
            alias_name=alias_name,
            phone=phone,
            ip_address=request.remote_addr
        )

        flash(f"Referral request successfully created! Your reference number is {referral.reference_number}.", "success")
        return redirect(url_for('referral.confirmation', referral_id=referral.id))

    return render_template(
        'referral/create.html',
        lang=lang,
        current_user=current_user,
        organization=org,
        opportunity=opp,
        profile=profile
    )

@referral_bp.route('/referral/confirmation/<int:referral_id>')
def confirmation(referral_id):
    lang = session.get('lang', 'en')
    current_user = get_current_user()
    referral = ReferralRequest.query.get_or_404(referral_id)
    return render_template(
        'referral/confirmation.html',
        lang=lang,
        current_user=current_user,
        referral=referral
    )

@referral_bp.route('/referral/track', methods=['GET', 'POST'])
def track_referral():
    lang = session.get('lang', 'en')
    current_user = get_current_user()

    ref_number = request.args.get('ref') or request.form.get('ref_number', '').strip()
    referral = None
    not_found = False

    if ref_number:
        referral = ReferralRequest.query.filter_by(reference_number=ref_number).first()
        if not referral:
            not_found = True

    return render_template(
        'referral/track.html',
        lang=lang,
        current_user=current_user,
        referral=referral,
        ref_number=ref_number,
        not_found=not_found
    )
