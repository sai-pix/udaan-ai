from datetime import datetime, timezone
import json
from app.extensions import db

class Opportunity(db.Model):
    __tablename__ = 'opportunities'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(180), nullable=False, index=True)
    opportunity_type = db.Column(db.String(50), nullable=False, default='job') # 'job', 'training', 'apprenticeship', 'daily_wage'
    description = db.Column(db.Text, nullable=True)
    employer_name = db.Column(db.String(150), nullable=False)
    location_locality = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=False, default='Visakhapatnam', index=True)
    wage_or_stipend = db.Column(db.String(100), nullable=True) # e.g. "₹14,000 / month" or "₹550 / day"
    hours_type = db.Column(db.String(50), default='full_time') # 'full_time', 'part_time', 'flexible', 'daily'
    requirements_skills_json = db.Column(db.Text, default='[]')
    requirements_education = db.Column(db.String(100), default='No formal degree required')
    requirements_documentation = db.Column(db.String(150), default='Basic identity or Aadhaar assistance acceptable')
    prerequisites = db.Column(db.Text, nullable=True) # e.g. "Basic physical fitness, punctual"
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    verification_status = db.Column(db.String(30), default='verified') # 'verified', 'unverified', 'pending_review'
    last_verified_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_demo_data = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    referrals = db.relationship('ReferralRequest', backref='opportunity', lazy=True)
    pathway_steps = db.relationship('PathwayStep', backref='opportunity', lazy=True)

    @property
    def requirements_skills(self):
        try:
            return json.loads(self.requirements_skills_json) if self.requirements_skills_json else []
        except Exception:
            return []

    @requirements_skills.setter
    def requirements_skills(self, value):
        self.requirements_skills_json = json.dumps(value if isinstance(value, list) else [value])

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'organization_name': self.organization.name if self.organization else None,
            'title': self.title,
            'opportunity_type': self.opportunity_type,
            'description': self.description,
            'employer_name': self.employer_name,
            'location_locality': self.location_locality,
            'city': self.city,
            'wage_or_stipend': self.wage_or_stipend,
            'hours_type': self.hours_type,
            'requirements_skills': self.requirements_skills,
            'requirements_education': self.requirements_education,
            'requirements_documentation': self.requirements_documentation,
            'prerequisites': self.prerequisites,
            'is_active': self.is_active,
            'verification_status': self.verification_status,
            'last_verified_date': self.last_verified_date.strftime('%Y-%m-%d') if self.last_verified_date else None,
            'is_demo_data': self.is_demo_data
        }
