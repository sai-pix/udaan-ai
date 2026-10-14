from datetime import datetime, timezone
from app.extensions import db

class Pathway(db.Model):
    __tablename__ = 'pathways'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('support_seeker_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), default='Personalized Barrier-Aware Livelihood Pathway')
    summary = db.Column(db.Text, nullable=True)
    total_steps = db.Column(db.Integer, default=6)
    current_step_index = db.Column(db.Integer, default=1)
    status = db.Column(db.String(30), default='active') # 'active', 'completed', 'abandoned'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    steps = db.relationship('PathwayStep', backref='pathway', cascade='all, delete-orphan', order_by='PathwayStep.step_order', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'title': self.title,
            'summary': self.summary,
            'total_steps': self.total_steps,
            'current_step_index': self.current_step_index,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'steps': [s.to_dict() for s in self.steps]
        }

class PathwayStep(db.Model):
    __tablename__ = 'pathway_steps'

    id = db.Column(db.Integer, primary_key=True)
    pathway_id = db.Column(db.Integer, db.ForeignKey('pathways.id', ondelete='CASCADE'), nullable=False)
    step_order = db.Column(db.Integer, nullable=False) # 1 to 6
    purpose = db.Column(db.String(200), nullable=False)
    recommended_action = db.Column(db.Text, nullable=False)
    
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id', ondelete='SET NULL'), nullable=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id', ondelete='SET NULL'), nullable=True)
    
    reason = db.Column(db.Text, nullable=True)
    verification_status = db.Column(db.String(30), default='verified')
    human_confirmation_required = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(30), default='pending') # 'pending', 'in_progress', 'completed', 'skipped'
    user_notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'pathway_id': self.pathway_id,
            'step_order': self.step_order,
            'purpose': self.purpose,
            'recommended_action': self.recommended_action,
            'resource_id': self.resource_id,
            'resource_name': self.resource.name if self.resource else None,
            'opportunity_id': self.opportunity_id,
            'opportunity_title': self.opportunity.title if self.opportunity else None,
            'reason': self.reason,
            'verification_status': self.verification_status,
            'human_confirmation_required': self.human_confirmation_required,
            'status': self.status,
            'user_notes': self.user_notes
        }
