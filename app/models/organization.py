from datetime import datetime, timezone
import json
from app.extensions import db

class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False, index=True)
    org_type = db.Column(db.String(50), nullable=False) # 'ngo', 'shelter', 'training_provider', 'employer', 'welfare_center'
    description = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    locality = db.Column(db.String(100), nullable=True, index=True)
    city = db.Column(db.String(100), nullable=False, default='Visakhapatnam', index=True)
    state = db.Column(db.String(100), nullable=False, default='Andhra Pradesh')
    pincode = db.Column(db.String(20), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    official_website = db.Column(db.String(255), nullable=True)
    services_offered_json = db.Column(db.Text, default='[]')
    eligibility_criteria = db.Column(db.Text, nullable=True)
    opening_hours = db.Column(db.String(150), nullable=True)
    capacity_status = db.Column(db.String(30), default='available') # 'available', 'limited', 'full', 'unknown'
    verification_status = db.Column(db.String(30), default='verified') # 'verified', 'unverified', 'pending_review', 'deactivated'
    last_verified_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    verification_source = db.Column(db.String(150), default='Community Pilot Audit')
    internal_notes = db.Column(db.Text, nullable=True)
    is_demo_data = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    resources = db.relationship('Resource', backref='organization', cascade='all, delete-orphan', lazy=True)
    opportunities = db.relationship('Opportunity', backref='organization', cascade='all, delete-orphan', lazy=True)
    referrals = db.relationship('ReferralRequest', backref='organization', lazy=True)

    @property
    def services_offered(self):
        try:
            return json.loads(self.services_offered_json) if self.services_offered_json else []
        except Exception:
            return []

    @services_offered.setter
    def services_offered(self, value):
        self.services_offered_json = json.dumps(value if isinstance(value, list) else [value])

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'org_type': self.org_type,
            'description': self.description,
            'address': self.address,
            'locality': self.locality,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'contact_phone': self.contact_phone,
            'official_website': self.official_website,
            'services_offered': self.services_offered,
            'eligibility_criteria': self.eligibility_criteria,
            'opening_hours': self.opening_hours,
            'capacity_status': self.capacity_status,
            'verification_status': self.verification_status,
            'last_verified_date': self.last_verified_date.strftime('%Y-%m-%d') if self.last_verified_date else None,
            'verification_source': self.verification_source,
            'is_demo_data': self.is_demo_data
        }
