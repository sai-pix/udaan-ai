from datetime import datetime, timezone
from app.extensions import db

class AuditEvent(db.Model):
    __tablename__ = 'audit_events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action_type = db.Column(db.String(80), nullable=False, index=True) # e.g., 'VERIFY_ORG', 'UPDATE_REFERRAL', 'DELETE_PROFILE'
    entity_type = db.Column(db.String(80), nullable=False) # 'organization', 'resource', 'referral', 'profile'
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True) # Sanitized details without sensitive PII
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }
