import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure parent path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.organization import Organization
from app.models.resource import Resource
from app.models.opportunity import Opportunity
from app.models.seeker_profile import SupportSeekerProfile
from app.models.pathway import Pathway, PathwayStep
from app.models.referral import ReferralRequest
from app.models.followup import FollowUpRecord
from app.models.audit import AuditEvent

def seed_database():
    app = create_app()
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()

        # Clear existing demo data to ensure clean idempotency
        try:
            FollowUpRecord.query.delete()
            ReferralRequest.query.delete()
            PathwayStep.query.delete()
            Pathway.query.delete()
            SupportSeekerProfile.query.delete()
            Opportunity.query.delete()
            Resource.query.delete()
            User.query.delete()
            Organization.query.delete()
            AuditEvent.query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()

        print("[Seed] Seeding Organizations...")
        # 1. Karuna Shelter & Livelihood Trust (NGO)
        org_karuna = Organization(
            name="Karuna Livelihood & Shelter Trust [DEMO DATA]",
            org_type="ngo",
            description="Grassroots NGO providing emergency night shelter, hot meals, and social casework for displaced and homeless adults in Coastal Andhra.",
            address="Near Old Post Office, Daba Gardens",
            locality="Daba Gardens",
            city="Visakhapatnam",
            state="Andhra Pradesh",
            pincode="530020",
            contact_phone="+91 891 2500001",
            official_website="https://demo.karunatrust.org",
            services_offered=["Emergency Shelter", "Community Kitchen", "Casework Support", "Healthcare Referral"],
            eligibility_criteria="Any adult experiencing acute shelter insecurity or economic crisis. No fee charged.",
            opening_hours="Shelter intake: 6:00 PM – 9:00 PM; Office: 9:00 AM – 5:00 PM",
            capacity_status="available",
            verification_status="verified",
            verification_source="Visakhapatnam Urban Community Development Cell (Pilot Audit)",
            internal_notes="Verified demo NGO with 40-bed night shelter capacity.",
            is_demo_data=True
        )

        # 2. Andhra Prerana Skill Development Society (Training Provider)
        org_prerana = Organization(
            name="Andhra Prerana Skill Development Society [DEMO DATA]",
            org_type="training_provider",
            description="Community vocational institute delivering subsidized and free skill development courses accredited by state mission standards.",
            address="Beside Bus Station, Benz Circle",
            locality="Benz Circle",
            city="Vijayawada",
            state="Andhra Pradesh",
            pincode="520010",
            contact_phone="+91 866 2400002",
            official_website="https://demo.preranaskills.org",
            services_offered=["Free Electrical Repair Training", "Industrial Tailoring", "Basic Computer Skills"],
            eligibility_criteria="Age 18–45, economic vulnerability, motivation to complete 3-week practical module.",
            opening_hours="Mon–Sat: 8:30 AM – 5:30 PM",
            capacity_status="available",
            verification_status="verified",
            verification_source="APSSDC Pilot Partner Registry",
            is_demo_data=True
        )

        # 3. Navajeevan Welfare & Documentation Centre (Welfare Center)
        org_navajeevan = Organization(
            name="Navajeevan Welfare & Documentation Centre [DEMO DATA]",
            org_type="welfare_center",
            description="Citizen facilitation centre supporting vulnerable residents with Aadhaar card enrollment, Jan Dhan zero-balance bank accounts, and ration entitlements.",
            address="Near Collectorate Road, Brodipet",
            locality="Brodipet",
            city="Guntur",
            state="Andhra Pradesh",
            pincode="522002",
            contact_phone="+91 863 2300003",
            official_website="https://demo.navajeevanwelfare.org",
            services_offered=["Aadhaar Assistance", "Jan Dhan Bank Account Help", "Welfare Scheme Access"],
            eligibility_criteria="Free facilitation for all low-income residents and unorganized workers.",
            opening_hours="Mon–Fri: 9:30 AM – 4:00 PM",
            capacity_status="available",
            verification_status="verified",
            verification_source="Civil Supplies & Welfare Audit Panel",
            is_demo_data=True
        )

        # 4. Coastal Logistics & Facility Services (Employer)
        org_coastal = Organization(
            name="Coastal Logistics & Facility Services [DEMO DATA]",
            org_type="employer",
            description="Verified private employer providing commercial facility maintenance, housekeeping, and warehouse operations across Visakhapatnam port corridor.",
            address="Harbour Industrial Estate, Gajuwaka",
            locality="Gajuwaka",
            city="Visakhapatnam",
            state="Andhra Pradesh",
            pincode="530026",
            contact_phone="+91 891 2700004",
            official_website="https://demo.coastallogistics.in",
            services_offered=["Fair-Wage Employment", "On-the-job Training", "Safety Gear Provided", "Provident Fund / ESI"],
            eligibility_criteria="Adults willing to perform physical work; zero previous formal qualification necessary for entry roles.",
            opening_hours="Mon–Sat: 8:00 AM – 6:00 PM",
            capacity_status="available",
            verification_status="verified",
            verification_source="District Employment Exchange & Labor Office",
            is_demo_data=True
        )

        # 5. Deccan Agri-Processing Hub (Employer)
        org_deccan = Organization(
            name="Deccan Agri-Processing Hub [DEMO DATA]",
            org_type="employer",
            description="Food packing and agro-produce distribution facility offering daily-wage and weekly-contract opportunities.",
            address="Auto Nagar Industrial Area",
            locality="Auto Nagar",
            city="Vijayawada",
            state="Andhra Pradesh",
            pincode="520007",
            contact_phone="+91 866 2500005",
            official_website="https://demo.deccanagri.org",
            services_offered=["Daily Wage Work", "Food Prep & Packaging", "Subsidized Lunch"],
            eligibility_criteria="Basic physical endurance, willingness to follow hygiene guidelines.",
            opening_hours="Mon–Sat: 7:00 AM – 4:00 PM",
            capacity_status="available",
            verification_status="verified",
            verification_source="AP Agro-Processing Forum",
            is_demo_data=True
        )

        # 6. Unverified sample employer (to demonstrate verification filters)
        org_unverified = Organization(
            name="Sri Venkateswara Private Contracts [DEMO DATA]",
            org_type="employer",
            description="Independent contracting firm offering occasional loading and transport labor.",
            address="Railway Colony, Tirupati",
            locality="Railway Colony",
            city="Tirupati",
            state="Andhra Pradesh",
            pincode="517501",
            contact_phone="+91 877 2200006",
            services_offered=["Casual Labor"],
            capacity_status="unknown",
            verification_status="pending_review",
            verification_source="Self-Registered Web Application",
            is_demo_data=True
        )

        db.session.add_all([org_karuna, org_prerana, org_navajeevan, org_coastal, org_deccan, org_unverified])
        db.session.flush()

        print("[Seed] Seeding Resources...")
        # Resources for Karuna
        res_shelter = Resource(
            organization_id=org_karuna.id,
            name="Karuna Dignity Night Shelter [DEMO DATA]",
            category="shelter",
            description="Safe, clean, supervised dormitory beds with lockers, clean drinking water, and shower facilities for unhoused adults.",
            eligibility_criteria="Open to adults in need of immediate shelter. No alcohol or substance use on premises.",
            locality="Daba Gardens",
            city="Visakhapatnam",
            contact_phone="+91 891 2500001",
            verified=True,
            capacity_status="available",
            is_demo_data=True
        )
        res_food = Resource(
            organization_id=org_karuna.id,
            name="Karuna Community Nutrition Canteen [DEMO DATA]",
            category="food",
            description="Nutritious hot vegetarian meals served twice daily (12:30 PM and 7:30 PM) at zero cost for seekers.",
            eligibility_criteria="Open to anyone experiencing hunger or food insecurity.",
            locality="Daba Gardens",
            city="Visakhapatnam",
            contact_phone="+91 891 2500001",
            verified=True,
            capacity_status="available",
            is_demo_data=True
        )

        # Resources for Prerana
        res_training_elec = Resource(
            organization_id=org_prerana.id,
            name="Free Practical Electrical Maintenance Course [DEMO DATA]",
            category="training",
            description="3-week hands-on training on domestic wiring, appliance servicing, and safety standards with free toolkits upon graduation.",
            eligibility_criteria="Ages 18-40. Free course sponsored under livelihood inclusion grants.",
            locality="Benz Circle",
            city="Vijayawada",
            contact_phone="+91 866 2400002",
            verified=True,
            capacity_status="available",
            is_demo_data=True
        )
        res_training_tailor = Resource(
            organization_id=org_prerana.id,
            name="Garment Construction & Tailoring Workshop [DEMO DATA]",
            category="training",
            description="4-week vocational sewing and tailoring workshop for immediate garment industry hiring.",
            eligibility_criteria="Open to all interested candidates. Stipend provided for travel.",
            locality="Benz Circle",
            city="Vijayawada",
            contact_phone="+91 866 2400002",
            verified=True,
            capacity_status="available",
            is_demo_data=True
        )

        # Resources for Navajeevan
        res_doc_desk = Resource(
            organization_id=org_navajeevan.id,
            name="Jan Dhan & Aadhaar Facilitation Helpdesk [DEMO DATA]",
            category="documentation",
            description="Dedicated social workers helping obtain duplicate Aadhaar letters, open zero-balance bank accounts, and register for labor welfare cards.",
            eligibility_criteria="Any unorganized worker or homeless individual needing documentation.",
            locality="Brodipet",
            city="Guntur",
            contact_phone="+91 863 2300003",
            verified=True,
            capacity_status="available",
            is_demo_data=True
        )

        db.session.add_all([res_shelter, res_food, res_training_elec, res_training_tailor, res_doc_desk])
        db.session.flush()

        print("[Seed] Seeding Opportunities...")
        # Opportunities at Coastal Logistics
        opp_cleaner = Opportunity(
            organization_id=org_coastal.id,
            title="Commercial Facility Caretaker & Cleaning Assistant [DEMO DATA]",
            opportunity_type="job",
            description="Cleaning, waste segregation, floor maintenance, and basic sanitation for commercial port facilities. Protective boots and gloves provided.",
            employer_name="Coastal Logistics & Facility Services",
            location_locality="Gajuwaka",
            city="Visakhapatnam",
            wage_or_stipend="₹13,500 / month (Paid weekly or monthly)",
            hours_type="full_time",
            requirements_skills=["Cleaning", "Sanitation", "Physical Stamina", "Punctuality"],
            requirements_education="No formal degree required; ability to follow spoken instructions",
            requirements_documentation="Aadhaar or local verification assistance accepted on joining",
            prerequisites="Ability to stand for 6 hours; punctual morning arrival",
            is_active=True,
            verification_status="verified",
            is_demo_data=True
        )
        opp_warehouse = Opportunity(
            organization_id=org_coastal.id,
            title="Warehouse Inventory & Packing Assistant [DEMO DATA]",
            opportunity_type="job",
            description="Box sorting, carton labeling, basic inventory recording, and pallet movement inside modern ventilated warehouse.",
            employer_name="Coastal Logistics & Facility Services",
            location_locality="Gajuwaka",
            city="Visakhapatnam",
            wage_or_stipend="₹15,000 / month + ₹1,000 attendance bonus",
            hours_type="full_time",
            requirements_skills=["Warehouse", "Packing", "Physical Stamina", "Basic Numerical Sense"],
            requirements_education="No formal degree required",
            requirements_documentation="Aadhaar card needed for insurance compliance (help provided)",
            prerequisites="Comfortable with lifting up to 15 kg boxes",
            is_active=True,
            verification_status="verified",
            is_demo_data=True
        )

        # Opportunities at Deccan Agri
        opp_food_helper = Opportunity(
            organization_id=org_deccan.id,
            title="Food Preparation & Packaging Helper [DEMO DATA]",
            opportunity_type="daily_wage",
            description="Washing, sorting, cutting, and packaging produce. Daily cash wage distributed at 4:30 PM each evening.",
            employer_name="Deccan Agri-Processing Hub",
            location_locality="Auto Nagar",
            city="Vijayawada",
            wage_or_stipend="₹550 / day + Daily lunch provided",
            hours_type="daily",
            requirements_skills=["Cooking", "Kitchen Assistance", "Food Prep", "Hygiene"],
            requirements_education="None required",
            requirements_documentation="Voluntary identity verification",
            prerequisites="Adherence to clean hands and hair net safety norms",
            is_active=True,
            verification_status="verified",
            is_demo_data=True
        )

        # Opportunity at Unverified Firm
        opp_unverified_job = Opportunity(
            organization_id=org_unverified.id,
            title="Loading & Transport Helper (Unverified Listing) [DEMO DATA]",
            opportunity_type="job",
            description="Loading bags into transport vehicles. Note: Listing has not yet completed Udaan community wage audit.",
            employer_name="Sri Venkateswara Private Contracts",
            location_locality="Railway Colony",
            city="Tirupati",
            wage_or_stipend="₹400 / day",
            hours_type="daily",
            requirements_skills=["Loading", "Physical Stamina"],
            requirements_education="None",
            requirements_documentation="None",
            prerequisites="Physical strength",
            is_active=True,
            verification_status="pending_review",
            is_demo_data=True
        )

        db.session.add_all([opp_cleaner, opp_warehouse, opp_food_helper, opp_unverified_job])
        db.session.flush()

        print("[Seed] Seeding Demo Users...")
        # 1. Admin
        admin_user = User(
            username="admin",
            email="admin@udaan.demo",
            role="admin",
            is_active=True
        )
        admin_user.set_password("DemoAdmin2026!")

        # 2. NGO Staff (Karuna)
        ngo_staff_user = User(
            username="karuna_staff",
            email="karuna.staff@udaan.demo",
            role="ngo_staff",
            organization_id=org_karuna.id,
            is_active=True
        )
        ngo_staff_user.set_password("DemoKaruna2026!")

        # 3. Employer (Coastal Logistics)
        employer_user = User(
            username="coastal_hr",
            email="coastal.hr@udaan.demo",
            role="employer",
            organization_id=org_coastal.id,
            is_active=True
        )
        employer_user.set_password("DemoCoastal2026!")

        # 4. Support Seeker User
        seeker_user = User(
            username="raju_seeker",
            email="seeker@udaan.demo",
            role="seeker",
            is_active=True
        )
        seeker_user.set_password("DemoSeeker2026!")

        db.session.add_all([admin_user, ngo_staff_user, employer_user, seeker_user])
        db.session.flush()

        print("[Seed] Seeding Realistic Support-Seeker Profile & Pathway...")
        # Fictional Support Seeker: Raju V. (Andhra Pradesh pilot scenario)
        demo_profile = SupportSeekerProfile(
            user_id=seeker_user.id,
            alias_name="Raju V.",
            preferred_language="te",
            contact_phone="+91 98480 12345",
            skills=["Cleaning & Sanitation", "General Physical Work", "Basic Kitchen Assistance"],
            experience_summary="2 years doing shop cleaning and helper work; lost accommodation during recent displacement.",
            preferred_job_types=["Cleaning", "Helper", "Facility Maintenance"],
            preferred_locality="Gajuwaka",
            city="Visakhapatnam",
            availability="immediate",
            practical_barriers=["shelter_needed", "no_documentation", "training_cost_barrier"],
            requested_support=["shelter", "job", "documentation"],
            accessibility_needs="Prefers day-time work due to lack of night transit.",
            raw_natural_input="I used to do cleaning and physical loading in shops. I currently sleep outside near the station and have no Aadhaar card copy with me. I need safe place to sleep and an immediate fair cleaning job in Vizag.",
            ai_assisted=False,
            consent_given=True,
            consent_timestamp=datetime.now(timezone.utc)
        )
        db.session.add(demo_profile)
        db.session.flush()

        # Seed realistic Pathway
        pathway = Pathway(
            profile_id=demo_profile.id,
            title="Personalized Livelihood Pathway for Raju V.",
            summary="Barrier-aware 6-step roadmap addressing acute shelter and Aadhaar documentation while securing fair-wage employment in Visakhapatnam.",
            total_steps=6,
            current_step_index=2,
            status="active"
        )
        db.session.add(pathway)
        db.session.flush()

        # Steps
        s1 = PathwayStep(
            pathway_id=pathway.id,
            step_order=1,
            purpose="Urgent Shelter & Night Accommodation",
            recommended_action=f"Check into {res_shelter.name} at Daba Gardens to secure safe dormitory bed and warm meals.",
            resource_id=res_shelter.id,
            reason="Safe sleep and security are necessary prerequisites before beginning daily work.",
            verification_status="verified",
            human_confirmation_required=True,
            status="completed",
            user_notes="Checked in with volunteer Krishna; bed assigned."
        )

        s2 = PathwayStep(
            pathway_id=pathway.id,
            step_order=2,
            purpose="Documentation & Financial Inclusion",
            recommended_action=f"Visit {res_doc_desk.name} for free Aadhaar retrieval and zero-balance Jan Dhan bank account setup.",
            resource_id=res_doc_desk.id,
            reason="Having an official bank account allows direct weekly payroll wage deposits.",
            verification_status="verified",
            human_confirmation_required=True,
            status="in_progress"
        )

        s3 = PathwayStep(
            pathway_id=pathway.id,
            step_order=3,
            purpose="Practical Skill Readiness",
            recommended_action="Participate in 1-day facility sanitation and chemical safety orientation.",
            reason="Ensures immediate safety protocols when working around commercial machinery.",
            verification_status="verified",
            human_confirmation_required=False,
            status="pending"
        )

        s4 = PathwayStep(
            pathway_id=pathway.id,
            step_order=4,
            purpose="Realistic Livelihood Opportunity Application",
            recommended_action=f"Target opening: '{opp_cleaner.title}' at {opp_cleaner.employer_name} ({opp_cleaner.wage_or_stipend}).",
            opportunity_id=opp_cleaner.id,
            reason="Top algorithmic match: aligns with your cleaning experience, immediate availability, and Gajuwaka locality.",
            verification_status="verified",
            human_confirmation_required=True,
            status="pending"
        )

        s5 = PathwayStep(
            pathway_id=pathway.id,
            step_order=5,
            purpose="Direct Contact & Consented Referral",
            recommended_action="Submit consent-based referral request to Coastal Logistics & Facility Services HR coordinator.",
            opportunity_id=opp_cleaner.id,
            reason="Ensures your consented profile is reviewed respectfully by employer staff without exposing private history.",
            verification_status="verified",
            human_confirmation_required=True,
            status="pending"
        )

        s6 = PathwayStep(
            pathway_id=pathway.id,
            step_order=6,
            purpose="Outcome Tracking & Retention Support",
            recommended_action="Caseworker check-in at 7 days and 30 days to review wage receipts, transit stability, and accommodation.",
            reason="Sustaining initial employment requires rapid resolution of unexpected hurdles.",
            verification_status="verified",
            human_confirmation_required=True,
            status="pending"
        )

        db.session.add_all([s1, s2, s3, s4, s5, s6])
        db.session.flush()

        print("[Seed] Seeding Sample Referral and Follow-ups...")
        # Seed an active referral for Raju V. to Coastal Logistics
        ref_code = "REF-2026-AP8F"
        demo_referral = ReferralRequest(
            reference_number=ref_code,
            profile_id=demo_profile.id,
            organization_id=org_coastal.id,
            opportunity_id=opp_cleaner.id,
            status="under_review",
            seeker_alias_or_name=demo_profile.alias_name,
            seeker_contact_phone=demo_profile.contact_phone,
            staff_notes="Consented profile reviewed by HR. Candidate matches commercial cleaning requirements. Scheduling orientation call.",
            consented_data_snapshot={
                'alias_name': demo_profile.alias_name,
                'contact_phone': demo_profile.contact_phone,
                'skills': demo_profile.skills,
                'city': demo_profile.city,
                'preferred_locality': demo_profile.preferred_locality,
                'availability': demo_profile.availability,
                'relevant_barriers': demo_profile.practical_barriers,
                'target_opportunity': opp_cleaner.title
            }
        )
        db.session.add(demo_referral)
        db.session.flush()

        # Follow-up for the referral
        fu1 = FollowUpRecord(
            referral_id=demo_referral.id,
            profile_id=demo_profile.id,
            milestone="referral_submitted",
            notes=f"Referral {ref_code} submitted with explicit seeker consent.",
            outcome_status="in_progress"
        )
        fu2 = FollowUpRecord(
            referral_id=demo_referral.id,
            profile_id=demo_profile.id,
            milestone="organization_contacted",
            notes="Coastal HR verified candidate availability for Gajuwaka facility.",
            outcome_status="in_progress"
        )
        db.session.add_all([fu1, fu2])

        # Audit events
        audit = AuditEvent(
            user_id=admin_user.id,
            action_type="SYSTEM_INITIALIZED",
            entity_type="system",
            details="Pilot scenario database seeded with synthetic Andhra Pradesh pilot data."
        )
        db.session.add(audit)

        db.session.commit()
        print("[Seed] Demo scenario successfully seeded!")

if __name__ == '__main__':
    seed_database()
