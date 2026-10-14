from datetime import datetime, timezone
from app.extensions import db

class FollowUpRecord(db.Model):
    __tablename__ = 'followup_records'

    id = db.Column(db.Integer, primary_key=True)
    referral_id = db.Column(db.Integer, db.ForeignKey('referral_requests.id', ondelete='CASCADE'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('support_seeker_profiles.id', ondelete='CASCADE'), nullable=False)
    
    # Milestone: referral_submitted, organization_contacted, appointment_confirmed, 
    # training_attended, application_submitted, employment_started, 
    # retention_30_days, retention_90_days, referral_failed
    milestone = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    outcome_status = db.Column(db.String(50), default='in_progress') # 'successful', 'in_progress', 'requires_alternative', 'closed'
    next_followup_date = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'referral_id': self.referral_id,
            'profile_id': self.profile_id,
            'milestone': self.milestone,
            'notes': self.notes,
            'outcome_status': self.outcome_status,
            'next_followup_date': self.next_followup_date.strftime('%Y-%m-%d') if self.next_followup_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }
