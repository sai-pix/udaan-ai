from datetime import datetime, timezone
from app.extensions import db

class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True) # 'shelter', 'food', 'rehabilitation', 'training', 'employment', 'documentation'
    description = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.Text, nullable=True)
    locality = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=False, default='Visakhapatnam', index=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    verified = db.Column(db.Boolean, default=True, nullable=False)
    last_verified_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    capacity_status = db.Column(db.String(30), default='available') # 'available', 'limited', 'full', 'unknown'
    is_demo_data = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    pathway_steps = db.relationship('PathwayStep', backref='resource', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'organization_name': self.organization.name if self.organization else None,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'eligibility_criteria': self.eligibility_criteria,
            'locality': self.locality,
            'city': self.city,
            'contact_phone': self.contact_phone,
            'verified': self.verified,
            'last_verified_date': self.last_verified_date.strftime('%Y-%m-%d') if self.last_verified_date else None,
            'capacity_status': self.capacity_status,
            'is_demo_data': self.is_demo_data
        }
