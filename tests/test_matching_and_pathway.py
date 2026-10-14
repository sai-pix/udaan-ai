from app.models.seeker_profile import SupportSeekerProfile
from app.models.opportunity import Opportunity
from app.models.resource import Resource
from app.models.pathway import PathwayStep
from app.services.matching_service import BarrierAwareMatchingEngine
from app.services.pathway_service import PathwayService
from app.extensions import db

def test_matching_engine_skill_and_location(app, seeded_data):
    with app.app_context():
        profile = SupportSeekerProfile(
            alias_name="Seeker Visakhapatnam",
            city="Visakhapatnam",
            preferred_locality="Daba Gardens",
            skills=["Cleaning", "Sanitation"],
            practical_barriers=["shelter_needed"],
            availability="immediate",
            consent_given=True
        )
        db.session.add(profile)
        db.session.commit()

        opps = Opportunity.query.all()
        matches = BarrierAwareMatchingEngine.match_opportunities(profile, opps)
        
        assert len(matches) > 0
        top_match = matches[0]
        assert top_match['opportunity'].city == "Visakhapatnam"
        assert top_match['score'] > 60
        assert any("Skills matched" in r for r in top_match['reasons'])
        assert any("Located in your target city" in r for r in top_match['reasons'])

def test_pathway_generation_addresses_concrete_barriers(app, seeded_data):
    with app.app_context():
        profile = SupportSeekerProfile(
            alias_name="Kishore K.",
            city="Visakhapatnam",
            skills=["Cleaning"],
            practical_barriers=["shelter_needed", "no_documentation"],
            requested_support=["shelter", "job"],
            consent_given=True
        )
        db.session.add(profile)
        db.session.commit()

        pathway = PathwayService.generate_pathway(profile)
        assert pathway is not None
        assert len(pathway.steps) == 6

        step1 = pathway.steps[0]
        assert step1.step_order == 1
        assert "Shelter" in step1.purpose
        assert step1.resource_id == seeded_data['res_shelter_id']

        step2 = pathway.steps[1]
        assert step2.step_order == 2
        assert "Documentation" in step2.purpose
        assert step2.resource_id == seeded_data['res_doc_id']

        step4 = pathway.steps[3]
        assert step4.step_order == 4
        assert step4.opportunity_id == seeded_data['opp_clean_id']

def test_pathway_step_status_toggle(client, app, seeded_data):
    with app.app_context():
        profile = SupportSeekerProfile(alias_name="Step Tester", city="Visakhapatnam", consent_given=True)
        db.session.add(profile)
        db.session.commit()
        pathway = PathwayService.generate_pathway(profile)
        step_id = pathway.steps[0].id

    res = client.post(f'/api/step/{step_id}/toggle', json={'status': 'completed'})
    assert res.status_code == 200
    assert res.json['status'] == 'completed'

    with app.app_context():
        updated_step = db.session.get(PathwayStep, step_id)
        assert updated_step.status == 'completed'
