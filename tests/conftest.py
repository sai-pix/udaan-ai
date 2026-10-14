import pytest
from app import create_app
from app.config import Config
from app.extensions import db
from app.models.user import User
from app.models.organization import Organization
from app.models.resource import Resource
from app.models.opportunity import Opportunity
from app.models.seeker_profile import SupportSeekerProfile
from app.models.referral import ReferralRequest
from app.models.pathway import Pathway, PathwayStep

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    DEMO_MODE = True
    ADMIN_SETUP_SECRET = 'TestBootstrapSecret123!'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        # Prevent DetachedInstanceError across test assertions
        db.session.expire_on_commit = False
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def seeded_data(app):
    with app.app_context():
        # Organization A: Karuna NGO
        org_a = Organization(
            name="Karuna Shelter Trust [TEST]",
            org_type="ngo",
            city="Visakhapatnam",
            locality="Daba Gardens",
            contact_phone="+91 891 0001",
            verification_status="verified",
            is_demo_data=True
        )
        # Organization B: Deccan Agri
        org_b = Organization(
            name="Deccan Agri Hub [TEST]",
            org_type="employer",
            city="Vijayawada",
            locality="Auto Nagar",
            contact_phone="+91 866 0002",
            verification_status="verified",
            is_demo_data=True
        )
        db.session.add_all([org_a, org_b])
        db.session.flush()

        # Users
        admin_u = User(username="test_admin", email="admin@test.com", role="admin")
        admin_u.set_password("AdminPass123!")

        ngo_u = User(username="ngo_staff_a", email="ngo@test.com", role="ngo_staff", organization_id=org_a.id)
        ngo_u.set_password("NgoPass123!")

        emp_u = User(username="emp_b", email="emp@test.com", role="employer", organization_id=org_b.id)
        emp_u.set_password("EmpPass123!")

        seeker_u = User(username="seeker_1", email="seeker@test.com", role="seeker")
        seeker_u.set_password("SeekerPass123!")

        db.session.add_all([admin_u, ngo_u, emp_u, seeker_u])
        db.session.flush()

        # Resources
        res_shelter = Resource(
            organization_id=org_a.id,
            name="Night Shelter [TEST]",
            category="shelter",
            city="Visakhapatnam",
            locality="Daba Gardens",
            verified=True
        )
        res_doc = Resource(
            organization_id=org_a.id,
            name="Aadhaar Helpdesk [TEST]",
            category="documentation",
            city="Visakhapatnam",
            locality="Daba Gardens",
            verified=True
        )
        db.session.add_all([res_shelter, res_doc])

        # Opportunity
        opp_clean = Opportunity(
            organization_id=org_a.id,
            title="Cleaning Staff [TEST]",
            opportunity_type="job",
            employer_name="Karuna Facility",
            city="Visakhapatnam",
            location_locality="Daba Gardens",
            wage_or_stipend="₹13,000 / month",
            requirements_skills=["Cleaning", "Sanitation"],
            is_active=True,
            verification_status="verified"
        )
        db.session.add(opp_clean)
        db.session.commit()

        # Refresh objects to ensure they are loaded
        return {
            'org_a_id': org_a.id,
            'org_b_id': org_b.id,
            'admin_u_id': admin_u.id,
            'ngo_u_id': ngo_u.id,
            'emp_u_id': emp_u.id,
            'seeker_u_id': seeker_u.id,
            'res_shelter_id': res_shelter.id,
            'res_doc_id': res_doc.id,
            'opp_clean_id': opp_clean.id,
            'org_a': org_a,
            'org_b': org_b,
            'admin_u': admin_u,
            'ngo_u': ngo_u,
            'emp_u': emp_u,
            'seeker_u': seeker_u,
            'res_shelter': res_shelter,
            'res_doc': res_doc,
            'opp_clean': opp_clean
        }
