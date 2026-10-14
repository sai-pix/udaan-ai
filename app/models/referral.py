from datetime import datetime, timezone
import json
import secrets
from app.extensions import db

class ReferralRequest(db.Model):
    __tablename__ = 'referral_requests'

    id = db.Column(db.Integer, primary_key=True)
    reference_number = db.Column(db.String(32), unique=True, nullable=False, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('support_seeker_profiles.id', ondelete='CASCADE'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id', ondelete='SET NULL'), nullable=True)
    
    # Status lifecycle: draft, submitted, under_review, accepted, contacted, appointment_scheduled, completed, declined, cancelled
    status = db.Column(db.String(30), default='submitted', nullable=False, index=True)
    
    consented_data_snapshot_json = db.Column(db.Text, default='{}')
    seeker_alias_or_name = db.Column(db.String(100), default='Community Member')
    seeker_contact_phone = db.Column(db.String(50), nullable=True)
    
    appointment_date = db.Column(db.DateTime, nullable=True)
    staff_notes = db.Column(db.Text, nullable=True)
    outcome_summary = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    followups = db.relationship('FollowUpRecord', backref='referral', cascade='all, delete-orphan', lazy=True)

    @staticmethod
    def generate_reference_number():
        """Generates a human-friendly unique referral code, e.g., REF-2026-9A3F"""
        hex_suffix = secrets.token_hex(3).upper()
        return f"REF-2026-{hex_suffix}"

    @property
    def consented_data_snapshot(self):
        try:
            return json.loads(self.consented_data_snapshot_json) if self.consented_data_snapshot_json else {}
        except Exception:
            return {}

    @consented_data_snapshot.setter
    def consented_data_snapshot(self, value):
        self.consented_data_snapshot_json = json.dumps(value if isinstance(value, dict) else {})

    def to_dict(self):
        return {
            'id': self.id,
            'reference_number': self.reference_number,
            'profile_id': self.profile_id,
            'organization_id': self.organization_id,
            'organization_name': self.organization.name if self.organization else None,
            'opportunity_id': self.opportunity_id,
            'opportunity_title': self.opportunity.title if self.opportunity else None,
            'status': self.status,
            'seeker_alias_or_name': self.seeker_alias_or_name,
            'seeker_contact_phone': self.seeker_contact_phone,
            'appointment_date': self.appointment_date.strftime('%Y-%m-%d %H:%M') if self.appointment_date else None,
            'staff_notes': self.staff_notes,
            'outcome_summary': self.outcome_summary,
            'consented_data_snapshot': self.consented_data_snapshot,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else None
        }
