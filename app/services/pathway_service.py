import logging
from app.extensions import db
from app.models.seeker_profile import SupportSeekerProfile
from app.models.pathway import Pathway, PathwayStep
from app.models.opportunity import Opportunity
from app.models.resource import Resource
from app.services.matching_service import BarrierAwareMatchingEngine

logger = logging.getLogger(__name__)

class PathwayService:
    @classmethod
    def generate_pathway(cls, profile: SupportSeekerProfile) -> Pathway:
        """
        Dynamically constructs a 6-step personalized pathway tailored to the seeker's
        concrete barriers, location, and verified database opportunities.
        """
        # Fetch all verified/active resources and opportunities
        all_opportunities = Opportunity.query.filter_by(is_active=True).all()
        all_resources = Resource.query.all()

        # Run matching engine
        matched_opps = BarrierAwareMatchingEngine.match_opportunities(profile, all_opportunities)
        categorized_res = BarrierAwareMatchingEngine.match_support_resources(profile, all_resources)

        top_opp = matched_opps[0]['opportunity'] if matched_opps else None
        barriers = set(profile.practical_barriers or [])
        requested = set(profile.requested_support or [])

        # Create or retrieve Pathway container
        pathway = Pathway(
            profile_id=profile.id,
            title=f"Livelihood Pathway for {profile.alias_name or 'Community Member'}",
            summary=f"Personalized 6-step roadmap addressing {len(barriers)} barrier(s) towards sustainable livelihood in {profile.city}.",
            total_steps=6,
            current_step_index=1,
            status='active'
        )
        db.session.add(pathway)
        db.session.flush()

        steps_data = []

        # =========================================================================
        # STEP 1: Urgent Safety & Basic Needs (Shelter & Food)
        # =========================================================================
        if 'shelter_needed' in barriers or 'shelter' in requested:
            shelter_res = categorized_res['shelter'][0] if categorized_res['shelter'] else None
            steps_data.append({
                'step_order': 1,
                'purpose': 'Urgent Shelter & Night Accommodation',
                'recommended_action': f"Check into {shelter_res.name if shelter_res else 'Local Community Night Shelter'} to secure safe, dignified rest before beginning daily work.",
                'resource_id': shelter_res.id if shelter_res else None,
                'opportunity_id': None,
                'reason': 'Stable, safe sleep is foundational to physical health, daily punctuality, and job retention.',
                'verification_status': 'verified' if (shelter_res and shelter_res.verified) else 'pending_review',
                'human_confirmation_required': True
            })
        elif 'food_insecurity' in barriers or 'food' in requested:
            food_res = categorized_res['food'][0] if categorized_res['food'] else None
            steps_data.append({
                'step_order': 1,
                'purpose': 'Immediate Nutrition & Meal Access',
                'recommended_action': f"Access community kitchen or nutrition center at {food_res.name if food_res else 'Local Community Canteen'}.",
                'resource_id': food_res.id if food_res else None,
                'opportunity_id': None,
                'reason': 'Adequate daily nutrition prevents exhaustion and supports active physical livelihood.',
                'verification_status': 'verified' if (food_res and food_res.verified) else 'pending_review',
                'human_confirmation_required': False
            })
        else:
            steps_data.append({
                'step_order': 1,
                'purpose': 'Baseline Stability Confirmation',
                'recommended_action': "Confirm immediate housing and nutrition are stable so you can focus on work readiness.",
                'resource_id': None,
                'opportunity_id': None,
                'reason': 'No acute shelter or food emergency identified in intake; proceeding directly to livelihood onboarding.',
                'verification_status': 'verified',
                'human_confirmation_required': False
            })

        # =========================================================================
        # STEP 2: Documentation & Financial Inclusion
        # =========================================================================
        doc_res = categorized_res['documentation'][0] if categorized_res['documentation'] else None
        if 'no_documentation' in barriers or 'documentation' in requested or 'no_bank_account' in barriers:
            action_text = f"Visit {doc_res.name if doc_res else 'Ward Sachivalayam / MeeSeva Help Desk'} for free Aadhaar update, Jan Dhan bank account opening, or temporary ID proof."
            reason_text = "Most registered employers require a bank account or basic identification to process legal wage payments."
        else:
            action_text = "Ensure you have a copy of your bank passbook or Aadhaar details ready for employer payroll registration."
            reason_text = "Having your payment details ready accelerates wage disbursements."

        steps_data.append({
            'step_order': 2,
            'purpose': 'Documentation & Financial Inclusion',
            'recommended_action': action_text,
            'resource_id': doc_res.id if doc_res else None,
            'opportunity_id': None,
            'reason': reason_text,
            'verification_status': 'verified' if (doc_res and doc_res.verified) else 'pending_review',
            'human_confirmation_required': True if ('no_documentation' in barriers) else False
        })

        # =========================================================================
        # STEP 3: Skill Verification or Free Vocational Training
        # =========================================================================
        train_res = categorized_res['training'][0] if categorized_res['training'] else None
        if 'training_cost_barrier' in barriers or 'training' in requested or not profile.skills:
            action_text = f"Enroll in free, sponsored vocational workshop at {train_res.name if train_res else 'Andhra Pradesh Skill Development Centre (APSSDC)'}."
            reason_text = "Hands-on, free vocational training enhances wage bargaining power without any debt."
        else:
            action_text = f"Review your existing skills ({', '.join(profile.skills[:3]) if profile.skills else 'General Skills'}) with a community volunteer to prepare a 1-page profile sheet."
            reason_text = "Clear articulation of your concrete abilities builds confidence during workplace onboarding."

        steps_data.append({
            'step_order': 3,
            'purpose': 'Practical Skill Readiness',
            'recommended_action': action_text,
            'resource_id': train_res.id if train_res else None,
            'opportunity_id': None,
            'reason': reason_text,
            'verification_status': 'verified' if (train_res and train_res.verified) else 'pending_review',
            'human_confirmation_required': False
        })

        # =========================================================================
        # STEP 4: Realistic Livelihood Opportunity Application
        # =========================================================================
        if top_opp:
            action_text = f"Target verified opening: '{top_opp.title}' at {top_opp.employer_name} ({top_opp.wage_or_stipend or 'Fair Wage'}). Location: {top_opp.location_locality}, {top_opp.city}."
            reason_text = f"Top algorithmic match based on your skills, {top_opp.hours_type.replace('_', ' ')} schedule, and locality proximity."
            opp_id = top_opp.id
            verif_stat = top_opp.verification_status
        else:
            action_text = "Explore community daily-wage or facility support opportunities through verified municipal help desks."
            reason_text = "No private openings currently available in the exact locality; exploring public community postings."
            opp_id = None
            verif_stat = 'verified'

        steps_data.append({
            'step_order': 4,
            'purpose': 'Realistic Livelihood Opportunity Application',
            'recommended_action': action_text,
            'resource_id': None,
            'opportunity_id': opp_id,
            'reason': reason_text,
            'verification_status': verif_stat,
            'human_confirmation_required': True
        })

        # =========================================================================
        # STEP 5: Direct Contact or Consent-Based Referral
        # =========================================================================
        steps_data.append({
            'step_order': 5,
            'purpose': 'Direct Contact & Consented Referral',
            'recommended_action': "Submit a privacy-consented referral request to the partner organization, or use verified phone/address for in-person meeting.",
            'resource_id': None,
            'opportunity_id': top_opp.id if top_opp else None,
            'reason': 'A human caseworker or employer HR coordinator will review your consented profile and schedule an interview.',
            'verification_status': 'verified',
            'human_confirmation_required': True
        })

        # =========================================================================
        # STEP 6: Post-Placement Follow-Up & Retention Support
        # =========================================================================
        steps_data.append({
            'step_order': 6,
            'purpose': 'Outcome Tracking & Retention Support',
            'recommended_action': "Check in with your caseworker after 7 days and 30 days of work to ensure safe conditions, on-time wages, and resolve any transit or accommodation hiccups.",
            'resource_id': None,
            'opportunity_id': None,
            'reason': 'Sustained livelihood retention requires ongoing support during the initial transition period.',
            'verification_status': 'verified',
            'human_confirmation_required': True
        })

        # Persist steps
        for s in steps_data:
            step = PathwayStep(
                pathway_id=pathway.id,
                step_order=s['step_order'],
                purpose=s['purpose'],
                recommended_action=s['recommended_action'],
                resource_id=s['resource_id'],
                opportunity_id=s['opportunity_id'],
                reason=s['reason'],
                verification_status=s['verification_status'],
                human_confirmation_required=s['human_confirmation_required'],
                status='in_progress' if s['step_order'] == 1 else 'pending'
            )
            db.session.add(step)

        db.session.commit()
        return pathway
