from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.extensions import db
from app.models.pathway import Pathway, PathwayStep
from app.models.seeker_profile import SupportSeekerProfile
from app.services.i18n_service import t
from app.auth_helper import get_current_user

pathway_bp = Blueprint('pathway', __name__)

@pathway_bp.route('/pathway/<int:pathway_id>')
def view_pathway(pathway_id):
    lang = session.get('lang', 'en')
    current_user = get_current_user()

    pathway = Pathway.query.get_or_404(pathway_id)
    profile = pathway.profile

    # Calculate completion metrics
    total_steps = len(pathway.steps)
    completed_steps = sum(1 for s in pathway.steps if s.status == 'completed')
    progress_percentage = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0

    return render_template(
        'pathway/view.html',
        lang=lang,
        current_user=current_user,
        pathway=pathway,
        profile=profile,
        completed_steps=completed_steps,
        total_steps=total_steps,
        progress_percentage=progress_percentage
    )

@pathway_bp.route('/pathway/step/<int:step_id>/status', methods=['POST'])
def update_step_status(step_id):
    step = PathwayStep.query.get_or_404(step_id)
    new_status = request.form.get('status') or (request.json.get('status') if request.is_json else None)

    if new_status in ('pending', 'in_progress', 'completed', 'skipped'):
        step.status = new_status
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'step_id': step.id, 'status': step.status})
        flash(f"Step {step.step_order} marked as {step.status}.", "success")
    else:
        if request.is_json:
            return jsonify({'error': 'Invalid status'}), 400
        flash("Invalid status specified.", "danger")

    return redirect(url_for('pathway.view_pathway', pathway_id=step.pathway_id))

@pathway_bp.route('/pathway/step/<int:step_id>/notes', methods=['POST'])
def update_step_notes(step_id):
    step = PathwayStep.query.get_or_404(step_id)
    notes = request.form.get('user_notes', '').strip()
    step.user_notes = notes
    db.session.commit()
    flash("Notes saved successfully.", "info")
    return redirect(url_for('pathway.view_pathway', pathway_id=step.pathway_id))
