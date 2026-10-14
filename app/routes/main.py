import os
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.extensions import db
from app.models.organization import Organization
from app.models.resource import Resource
from app.models.opportunity import Opportunity
from app.models.seeker_profile import SupportSeekerProfile
from app.models.pathway import Pathway
from app.models.referral import ReferralRequest
from app.services.i18n_service import t, PRACTICAL_BARRIERS, SUPPORT_CATEGORIES, PILOT_CITIES
from app.auth_helper import get_current_user

main_bp = Blueprint('main', __name__)

@main_bp.after_app_request
def add_cache_headers(response):
    """Adds caching headers for static assets to improve client-side efficiency."""
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response

@main_bp.route('/')
def index():
    lang = session.get('lang', 'en')
    current_user = get_current_user()
    
    total_resources = Resource.query.filter_by(verified=True).count()
    total_opps = Opportunity.query.filter_by(is_active=True).count()
    total_orgs = Organization.query.count()
    
    session_profile_id = session.get('profile_id')
    recent_pathway = None
    if session_profile_id:
        profile = db.session.get(SupportSeekerProfile, session_profile_id)
        if profile and profile.pathways:
            recent_pathway = profile.pathways[-1]

    return render_template(
        'index.html',
        lang=lang,
        current_user=current_user,
        total_resources=total_resources,
        total_opps=total_opps,
        total_orgs=total_orgs,
        recent_pathway=recent_pathway,
        pilot_cities=PILOT_CITIES
    )

@main_bp.route('/about')
def about():
    lang = session.get('lang', 'en')
    current_user = get_current_user()
    return render_template('about.html', lang=lang, current_user=current_user)

@main_bp.route('/resources')
def resources():
    lang = session.get('lang', 'en')
    current_user = get_current_user()
    
    category = request.args.get('category')
    city = request.args.get('city')
    query = request.args.get('q')

    res_query = Resource.query
    if category:
        res_query = res_query.filter_by(category=category)
    if city:
        res_query = res_query.filter_by(city=city)
    if query:
        res_query = res_query.filter(Resource.name.ilike(f'%{query}%') | Resource.description.ilike(f'%{query}%'))

    resources_list = res_query.order_by(Resource.verified.desc(), Resource.name.asc()).all()

    return render_template(
        'resources.html',
        lang=lang,
        current_user=current_user,
        resources=resources_list,
        categories=SUPPORT_CATEGORIES,
        pilot_cities=PILOT_CITIES,
        selected_category=category,
        selected_city=city,
        search_query=query
    )

@main_bp.route('/opportunities')
def opportunities():
    lang = session.get('lang', 'en')
    current_user = get_current_user()
    
    city = request.args.get('city')
    opp_type = request.args.get('type')

    opp_query = Opportunity.query.filter_by(is_active=True)
    if city:
        opp_query = opp_query.filter_by(city=city)
    if opp_type:
        opp_query = opp_query.filter_by(opportunity_type=opp_type)

    opps_list = opp_query.order_by(Opportunity.created_at.desc()).all()

    return render_template(
        'opportunities.html',
        lang=lang,
        current_user=current_user,
        opportunities=opps_list,
        pilot_cities=PILOT_CITIES,
        selected_city=city,
        selected_type=opp_type
    )

@main_bp.route('/set-language/<lang>')
def set_language(lang):
    if lang in ('en', 'te'):
        session['lang'] = lang
        flash(f"Language set to {'Telugu (తెలుగు)' if lang == 'te' else 'English'}.", "info")
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/privacy')
def privacy():
    lang = session.get('lang', 'en')
    current_user = get_current_user()
    return render_template('privacy.html', lang=lang, current_user=current_user)

@main_bp.route('/delete-my-data', methods=['POST'])
def delete_my_data():
    session_profile_id = session.get('profile_id')
    if session_profile_id:
        profile = db.session.get(SupportSeekerProfile, session_profile_id)
        if profile:
            db.session.delete(profile)
            db.session.commit()
        session.pop('profile_id', None)
        flash("Your profile and session data have been completely erased from the database.", "success")
    else:
        flash("No active profile data found in current session.", "info")
    return redirect(url_for('main.index'))

@main_bp.route('/load-demo-scenario')
def load_demo_scenario():
    from scripts.seed_demo import seed_database
    seed_database()
    flash("Demonstration scenario successfully reloaded with Andhra Pradesh pilot data!", "success")
    return redirect(url_for('main.index'))
