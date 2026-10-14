import json
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.extensions import db
from app.models.seeker_profile import SupportSeekerProfile
from app.services.ai_service import extract_profile_from_text
from app.services.pathway_service import PathwayService
from app.services.i18n_service import t, PRACTICAL_BARRIERS, SUPPORT_CATEGORIES, PILOT_CITIES
from app.auth_helper import get_current_user

intake_bp = Blueprint('intake', __name__)

@intake_bp.route('/intake', methods=['GET'])
def intake_form():
    lang = session.get('lang', 'en')
    current_user = get_current_user()

    existing_profile = None
    profile_id = session.get('profile_id')
    if profile_id:
        existing_profile = db.session.get(SupportSeekerProfile, profile_id)

    return render_template(
        'intake/form.html',
        lang=lang,
        current_user=current_user,
        existing_profile=existing_profile,
        barriers_list=PRACTICAL_BARRIERS,
        support_categories=SUPPORT_CATEGORIES,
        pilot_cities=PILOT_CITIES
    )

@intake_bp.route('/intake/analyze-text', methods=['POST'])
def analyze_text():
    data = request.get_json() or {}
    raw_text = data.get('description', '')
    lang = data.get('language') or session.get('lang', 'en')

    if not raw_text or len(raw_text.strip()) < 5:
        return jsonify({'error': 'Please provide a descriptive explanation of your situation.'}), 400

    extracted = extract_profile_from_text(raw_text, preferred_language=lang)
    return jsonify(extracted)

@intake_bp.route('/intake/submit', methods=['POST'])
def submit_intake():
    lang = session.get('lang', 'en')
    current_user = get_current_user()

    consent = request.form.get('consent_given')
    if not consent:
        flash("You must provide consent before your pathway can be created. We prioritize your privacy.", "danger")
        return redirect(url_for('intake.intake_form'))

    alias_name = request.form.get('alias_name', '').strip() or 'Community Member'
    contact_phone = request.form.get('contact_phone', '').strip() or None
    city = request.form.get('city', 'Visakhapatnam').strip()
    preferred_locality = request.form.get('preferred_locality', '').strip()
    availability = request.form.get('availability', 'immediate').strip()
    accessibility_needs = request.form.get('accessibility_needs', '').strip()
    raw_natural_input = request.form.get('raw_natural_input', '').strip()

    skills_raw = request.form.get('skills', '')
    skills = [s.strip() for s in skills_raw.split(',') if s.strip()] if skills_raw else []

    barriers = request.form.getlist('practical_barriers')
    requested_support = request.form.getlist('requested_support')

    structured_data_str = request.form.get('structured_data_json', '{}')
    try:
        structured_data = json.loads(structured_data_str)
    except Exception:
        structured_data = {}

    ai_assisted = (request.form.get('ai_assisted') == 'true')

    profile = SupportSeekerProfile(
        session_id=session.sid if hasattr(session, 'sid') else str(datetime.now().timestamp()),
        user_id=current_user.id if current_user else None,
        preferred_language=lang,
        alias_name=alias_name,
        contact_phone=contact_phone,
        skills=skills,
        preferred_job_types=[skills_raw] if skills_raw else ['Entry-level fair work'],
        preferred_locality=preferred_locality,
        city=city,
        availability=availability,
        practical_barriers=barriers,
        requested_support=requested_support,
        accessibility_needs=accessibility_needs,
        raw_natural_input=raw_natural_input,
        structured_data=structured_data,
        ai_assisted=ai_assisted,
        consent_given=True,
        consent_timestamp=datetime.now(timezone.utc)
    )

    db.session.add(profile)
    db.session.commit()

    session['profile_id'] = profile.id

    pathway = PathwayService.generate_pathway(profile)

    flash("Your barrier-aware pathway has been successfully generated!", "success")
    return redirect(url_for('pathway.view_pathway', pathway_id=pathway.id))
