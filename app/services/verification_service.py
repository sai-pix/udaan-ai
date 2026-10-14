from datetime import datetime, timezone
from app.extensions import db
from app.models.organization import Organization
from app.models.resource import Resource
from app.models.opportunity import Opportunity
from app.models.audit import AuditEvent

class VerificationService:
    @classmethod
    def verify_organization(cls, org_id: int, status: str, source: str, admin_user, internal_notes: str = None):
        org = Organization.query.get(org_id)
        if not org:
            raise ValueError(f"Organization {org_id} not found.")

        old_status = org.verification_status
        org.verification_status = status
        org.verification_source = source or 'Administrator Review'
        org.last_verified_date = datetime.now(timezone.utc)
        if internal_notes:
            org.internal_notes = internal_notes

        # Cascade status to child resources and opportunities if deactivated
        if status == 'deactivated':
            for r in org.resources:
                r.verified = False
            for o in org.opportunities:
                o.is_active = False

        audit = AuditEvent(
            user_id=admin_user.id if admin_user else None,
            action_type='ORG_VERIFICATION_UPDATED',
            entity_type='organization',
            entity_id=org.id,
            details=f"Status changed from {old_status} to {status}. Source: {source}"
        )
        db.session.add(audit)
        db.session.commit()
        return org

    @classmethod
    def verify_resource(cls, resource_id: int, is_verified: bool, admin_user):
        resource = Resource.query.get(resource_id)
        if not resource:
            raise ValueError(f"Resource {resource_id} not found.")

        resource.verified = is_verified
        resource.last_verified_date = datetime.now(timezone.utc)

        audit = AuditEvent(
            user_id=admin_user.id if admin_user else None,
            action_type='RESOURCE_VERIFICATION_UPDATED',
            entity_type='resource',
            entity_id=resource.id,
            details=f"Verified set to {is_verified}"
        )
        db.session.add(audit)
        db.session.commit()
        return resource

    @classmethod
    def verify_opportunity(cls, opportunity_id: int, status: str, admin_user):
        opp = Opportunity.query.get(opportunity_id)
        if not opp:
            raise ValueError(f"Opportunity {opportunity_id} not found.")

        opp.verification_status = status
        opp.last_verified_date = datetime.now(timezone.utc)

        audit = AuditEvent(
            user_id=admin_user.id if admin_user else None,
            action_type='OPP_VERIFICATION_UPDATED',
            entity_type='opportunity',
            entity_id=opp.id,
            details=f"Opportunity verification status set to {status}"
        )
        db.session.add(audit)
        db.session.commit()
        return opp
