from datetime import datetime, timezone
import json
from app.extensions import db

class SupportSeekerProfile(db.Model):
    __tablename__ = 'support_seeker_profiles'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), index=True, nullable=True) # Enables guest seekers to navigate without mandatory signup
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    preferred_language = db.Column(db.String(10), default='en') # 'en', 'te'
    alias_name = db.Column(db.String(100), default='Community Member') # Voluntary alias/name, never full legal KYC requirement
    contact_phone = db.Column(db.String(50), nullable=True) # Voluntary contact number for referral follow-up
    
    skills_json = db.Column(db.Text, default='[]')
    experience_summary = db.Column(db.Text, nullable=True)
    preferred_job_types_json = db.Column(db.Text, default='[]')
    preferred_locality = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), default='Visakhapatnam', index=True)
    availability = db.Column(db.String(50), default='immediate') # 'immediate', 'flexible', 'day_shift', 'night_shift', 'part_time'
    
    practical_barriers_json = db.Column(db.Text, default='[]') # e.g. ['shelter_needed', 'no_documentation', 'no_bank_account', 'travel_restricted', 'training_cost_barrier', 'caregiver_responsibility']
    requested_support_json = db.Column(db.Text, default='[]') # e.g. ['shelter', 'food', 'training', 'job', 'documentation']
    accessibility_needs = db.Column(db.Text, nullable=True)
    
    raw_natural_input = db.Column(db.Text, nullable=True)
    structured_data_json = db.Column(db.Text, default='{}')
    ai_assisted = db.Column(db.Boolean, default=False)
    
    consent_given = db.Column(db.Boolean, default=False, nullable=False)
    consent_timestamp = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    pathways = db.relationship('Pathway', backref='profile', cascade='all, delete-orphan', lazy=True)
    referrals = db.relationship('ReferralRequest', backref='profile', cascade='all, delete-orphan', lazy=True)

    @property
    def skills(self):
        try:
            return json.loads(self.skills_json) if self.skills_json else []
        except Exception:
            return []

    @skills.setter
    def skills(self, value):
        self.skills_json = json.dumps(value if isinstance(value, list) else [value])

    @property
    def preferred_job_types(self):
        try:
            return json.loads(self.preferred_job_types_json) if self.preferred_job_types_json else []
        except Exception:
            return []

    @preferred_job_types.setter
    def preferred_job_types(self, value):
        self.preferred_job_types_json = json.dumps(value if isinstance(value, list) else [value])

    @property
    def practical_barriers(self):
        try:
            return json.loads(self.practical_barriers_json) if self.practical_barriers_json else []
        except Exception:
            return []

    @practical_barriers.setter
    def practical_barriers(self, value):
        self.practical_barriers_json = json.dumps(value if isinstance(value, list) else [value])

    @property
    def requested_support(self):
        try:
            return json.loads(self.requested_support_json) if self.requested_support_json else []
        except Exception:
            return []

    @requested_support.setter
    def requested_support(self, value):
        self.requested_support_json = json.dumps(value if isinstance(value, list) else [value])

    @property
    def structured_data(self):
        try:
            return json.loads(self.structured_data_json) if self.structured_data_json else {}
        except Exception:
            return {}

    @structured_data.setter
    def structured_data(self, value):
        self.structured_data_json = json.dumps(value if isinstance(value, dict) else {})

    def to_dict(self):
        return {
            'id': self.id,
            'alias_name': self.alias_name,
            'preferred_language': self.preferred_language,
            'skills': self.skills,
            'experience_summary': self.experience_summary,
            'preferred_job_types': self.preferred_job_types,
            'preferred_locality': self.preferred_locality,
            'city': self.city,
            'availability': self.availability,
            'practical_barriers': self.practical_barriers,
            'requested_support': self.requested_support,
            'accessibility_needs': self.accessibility_needs,
            'ai_assisted': self.ai_assisted,
            'consent_given': self.consent_given,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }
