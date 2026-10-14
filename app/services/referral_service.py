import logging
from datetime import datetime, timezone
from app.extensions import db
from app.models.referral import ReferralRequest
from app.models.seeker_profile import SupportSeekerProfile
from app.models.organization import Organization
from app.models.opportunity import Opportunity
from app.models.followup import FollowUpRecord
from app.models.audit import AuditEvent

logger = logging.getLogger(__name__)

class ReferralService:
    ALLOWED_STATUSES = [
        'draft',
        'submitted',
        'under_review',
        'accepted',
        'contacted',
        'appointment_scheduled',
        'completed',
        'declined',
        'cancelled'
    ]

    @classmethod
    def create_referral(cls, profile_id: int, organization_id: int, opportunity_id: int = None,
                        alias_name: str = None, phone: str = None,
                        custom_consented_fields: dict = None, ip_address: str = None) -> ReferralRequest:
        profile = SupportSeekerProfile.query.get(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found.")

        org = Organization.query.get(organization_id)
        if not org:
            raise ValueError(f"Organization {organization_id} not found.")

        opp = Opportunity.query.get(opportunity_id) if opportunity_id else None

        # Build privacy-safe consented snapshot
        snapshot = {
            'alias_name': alias_name or profile.alias_name or 'Community Member',
            'contact_phone': phone or profile.contact_phone,
            'skills': profile.skills,
            'city': profile.city,
            'preferred_locality': profile.preferred_locality,
            'availability': profile.availability,
            'relevant_barriers': profile.practical_barriers,
            'requested_support': profile.requested_support,
            'target_opportunity_title': opp.title if opp else None,
            'consent_timestamp': datetime.now(timezone.utc).isoformat()
        }

        if custom_consented_fields:
            snapshot.update(custom_consented_fields)

        # Generate unique referral code
        ref_number = ReferralRequest.generate_reference_number()
        # Ensure uniqueness
        while ReferralRequest.query.filter_by(reference_number=ref_number).first():
            ref_number = ReferralRequest.generate_reference_number()

        referral = ReferralRequest(
            reference_number=ref_number,
            profile_id=profile.id,
            organization_id=org.id,
            opportunity_id=opp.id if opp else None,
            status='submitted',
            seeker_alias_or_name=snapshot['alias_name'],
            seeker_contact_phone=snapshot.get('contact_phone'),
            consented_data_snapshot=snapshot
        )
        db.session.add(referral)
        db.session.flush()

        # Create initial follow-up record
        followup = FollowUpRecord(
            referral_id=referral.id,
            profile_id=profile.id,
            milestone='referral_submitted',
            notes=f"Referral {ref_number} submitted to {org.name}.",
            outcome_status='in_progress'
        )
        db.session.add(followup)

        # Audit log
        audit = AuditEvent(
            user_id=profile.user_id,
            action_type='REFERRAL_SUBMITTED',
            entity_type='referral',
            entity_id=referral.id,
            details=f"Referral {ref_number} created for org_id {org.id}",
            ip_address=ip_address
        )
        db.session.add(audit)

        db.session.commit()
        return referral

    @classmethod
    def update_status(cls, referral_id: int, new_status: str, current_user, 
                      staff_notes: str = None, appointment_date: datetime = None,
                      outcome_summary: str = None, ip_address: str = None) -> ReferralRequest:
        referral = ReferralRequest.query.get(referral_id)
        if not referral:
            raise ValueError(f"Referral {referral_id} not found.")

        if new_status not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")

        # Strict Organization Isolation Check
        if current_user.role == 'ngo_staff':
            if referral.organization_id != current_user.organization_id:
                raise PermissionError("Access Denied: You cannot manage referrals for other organizations.")
        elif current_user.role == 'employer':
            if referral.organization_id != current_user.organization_id:
                raise PermissionError("Access Denied: You cannot view referrals outside your employer account.")
        elif current_user.role != 'admin':
            raise PermissionError("Unauthorized role for status transition.")

        old_status = referral.status
        referral.status = new_status
        if staff_notes:
            referral.staff_notes = staff_notes
        if appointment_date:
            referral.appointment_date = appointment_date
        if outcome_summary:
            referral.outcome_summary = outcome_summary

        # Add milestone to FollowUpRecord
        milestone_map = {
            'accepted': 'appointment_confirmed',
            'contacted': 'organization_contacted',
            'appointment_scheduled': 'appointment_confirmed',
            'completed': 'employment_started' if referral.opportunity_id else 'follow_up_completed',
            'declined': 'referral_failed',
            'cancelled': 'referral_failed'
        }
        
        milestone = milestone_map.get(new_status, f"status_{new_status}")
        followup = FollowUpRecord(
            referral_id=referral.id,
            profile_id=referral.profile_id,
            milestone=milestone,
            notes=staff_notes or f"Status shifted from {old_status} to {new_status}",
            outcome_status='successful' if new_status == 'completed' else ('requires_alternative' if new_status in ('declined', 'cancelled') else 'in_progress')
        )
        db.session.add(followup)

        # Audit log
        audit = AuditEvent(
            user_id=current_user.id,
            action_type='REFERRAL_STATUS_UPDATED',
            entity_type='referral',
            entity_id=referral.id,
            details=f"Status changed from {old_status} to {new_status}",
            ip_address=ip_address
        )
        db.session.add(audit)

        db.session.commit()
        return referral
