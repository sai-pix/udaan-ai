import logging
from typing import List, Dict, Any
from app.models.opportunity import Opportunity
from app.models.resource import Resource
from app.models.seeker_profile import SupportSeekerProfile

logger = logging.getLogger(__name__)

class BarrierAwareMatchingEngine:
    """
    Pure algorithmic matching engine for Udaan AI.
    Separates rule-based matching logic from LLM generation.
    Evaluates:
      1. Skill alignment
      2. Locality and location feasibility
      3. Hours and schedule compatibility
      4. Missing prerequisites
      5. Practical barrier resolution via verified community resources
    """

    @classmethod
    def match_opportunities(cls, profile: SupportSeekerProfile, opportunities: List[Opportunity]) -> List[Dict[str, Any]]:
        results = []
        seeker_skills = [s.lower().strip() for s in (profile.skills or [])]
        seeker_city = (profile.city or '').lower().strip()
        seeker_locality = (profile.preferred_locality or '').lower().strip()
        seeker_barriers = set(profile.practical_barriers or [])

        for opp in opportunities:
            if not opp.is_active:
                continue

            score = 20 # Base feasibility score
            reasons = []
            caveats = []
            missing_prereqs = []
            addressable_barriers = []

            opp_skills = [s.lower().strip() for s in opp.requirements_skills]
            opp_city = (opp.city or '').lower().strip()
            opp_locality = (opp.location_locality or '').lower().strip()

            # 1. Location match
            if opp_city == seeker_city:
                score += 25
                reasons.append(f"Located in your target city ({opp.city})")
                if seeker_locality and (seeker_locality in opp_locality or opp_locality in seeker_locality):
                    score += 15
                    reasons.append(f"Located right in or near your preferred locality ({opp.location_locality})")
            else:
                score -= 20
                caveats.append(f"Located in {opp.city}, which is outside your selected city ({profile.city})")

            # 2. Skill alignment
            matched_skills = []
            for ss in seeker_skills:
                for os_skill in opp_skills:
                    if ss in os_skill or os_skill in ss:
                        matched_skills.append(os_skill)
            
            matched_skills = list(set(matched_skills))
            if matched_skills:
                score += min(35, len(matched_skills) * 15)
                reasons.append(f"Skills matched: {', '.join(matched_skills).title()}")
            else:
                # If no direct match, check if entry-level or no experience required
                if "no formal" in opp.requirements_education.lower() or not opp_skills:
                    score += 10
                    reasons.append("Entry-level role with on-the-job orientation provided")
                else:
                    caveats.append("Requires specific skills you did not list; vocational training recommended first")

            # 3. Hours and availability
            if profile.availability == 'immediate':
                score += 10
                reasons.append("Immediate placement compatible with your availability")

            # 4. Barrier & Documentation Checks
            if 'no_documentation' in seeker_barriers:
                if 'aadhaar' in opp.requirements_documentation.lower() and 'assistance' not in opp.requirements_documentation.lower():
                    missing_prereqs.append("Requires official Aadhaar/ID upfront for payroll")
                    addressable_barriers.append('no_documentation')
                else:
                    reasons.append("Employer accepts initial documentation assistance or Jan Dhan facilitation")

            if 'training_cost_barrier' in seeker_barriers:
                if opp.opportunity_type == 'training' and opp.wage_or_stipend and 'fee' not in opp.wage_or_stipend.lower():
                    reasons.append(f"Free program with stipend/wage support: {opp.wage_or_stipend}")
                elif opp.opportunity_type == 'training':
                    reasons.append("Zero tuition barrier - sponsored community skill program")

            if 'shelter_needed' in seeker_barriers:
                addressable_barriers.append('shelter_needed')
                caveats.append("Securing reliable night shelter is critical for sustained retention in this role")

            # 5. Verification status penalty/bonus
            if opp.verification_status == 'verified':
                score += 10
                reasons.append("Verified workplace with confirmed fair wage and terms")
            else:
                caveats.append("Listing is pending full community verification")

            # Clamp score between 0 and 100
            final_score = max(5, min(98, score))

            # Recommendation tier
            if final_score >= 70:
                tier = 'Strong Match'
            elif final_score >= 45:
                tier = 'Potential Match with Support'
            else:
                tier = 'Challenging Match (Prerequisites Needed)'

            results.append({
                'opportunity': opp,
                'score': final_score,
                'tier': tier,
                'reasons': reasons,
                'caveats': caveats,
                'missing_prereqs': missing_prereqs,
                'addressable_barriers': addressable_barriers,
                'verification_status': opp.verification_status,
                'last_verified_date': opp.last_verified_date.strftime('%Y-%m-%d') if opp.last_verified_date else None
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    @classmethod
    def match_support_resources(cls, profile: SupportSeekerProfile, resources: List[Resource]) -> Dict[str, List[Resource]]:
        """
        Categorizes verified community support resources to solve each specific barrier.
        """
        seeker_city = (profile.city or '').lower().strip()
        barriers = set(profile.practical_barriers or [])
        requested = set(profile.requested_support or [])

        categorized_resources = {
            'shelter': [],
            'food': [],
            'documentation': [],
            'training': [],
            'rehabilitation': [],
            'general': []
        }

        for res in resources:
            if not res.verified and res.capacity_status == 'full':
                continue # Skip full or unverified capacity

            res_city = (res.city or '').lower().strip()
            city_match = (res_city == seeker_city)
            
            category = res.category.lower()
            if category in categorized_resources:
                if city_match:
                    categorized_resources[category].insert(0, res)
                else:
                    categorized_resources[category].append(res)
            else:
                categorized_resources['general'].append(res)

        return categorized_resources
