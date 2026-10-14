from app.models.organization import Organization
from app.models.resource import Resource
from app.models.audit import AuditEvent
from app.models.seeker_profile import SupportSeekerProfile
from app.extensions import db

def test_admin_organization_verification(client, app, seeded_data):
    # Log in as admin
    client.post('/login', data={'identifier': 'test_admin', 'password': 'AdminPass123!'})
    
    org_id = seeded_data['org_b_id']
    res = client.post(f'/admin/organization/{org_id}/verify', data={
        'status': 'verified',
        'verification_source': 'District Labor Board Audit'
    }, follow_redirects=True)

    assert res.status_code == 200
    with app.app_context():
        org = Organization.query.get(org_id)
        assert org.verification_status == 'verified'
        assert org.verification_source == 'District Labor Board Audit'
        # Audit event created
        audit = AuditEvent.query.filter_by(entity_type='organization', entity_id=org_id).first()
        assert audit is not None
        assert audit.action_type == 'ORG_VERIFICATION_UPDATED'

def test_admin_resource_verification_toggle(client, app, seeded_data):
    client.post('/login', data={'identifier': 'test_admin', 'password': 'AdminPass123!'})
    
    res_id = seeded_data['res_shelter_id']
    # Toggle verification
    client.post(f'/admin/resource/{res_id}/toggle-verify', follow_redirects=True)
    with app.app_context():
        res = Resource.query.get(res_id)
        assert res.verified is False

    # Toggle back
    client.post(f'/admin/resource/{res_id}/toggle-verify', follow_redirects=True)
    with app.app_context():
        res = Resource.query.get(res_id)
        assert res.verified is True

def test_right_to_erasure_deletes_profile(client, app, seeded_data):
    # Create profile in session
    client.post('/intake/submit', data={
        'alias_name': 'Erasure Subject',
        'city': 'Visakhapatnam',
        'consent_given': 'yes'
    })

    with app.app_context():
        profile = SupportSeekerProfile.query.filter_by(alias_name='Erasure Subject').first()
        assert profile is not None
        p_id = profile.id

    # Post to delete data
    res = client.post('/delete-my-data', follow_redirects=True)
    assert res.status_code == 200
    assert b"erased from the database" in res.data

    with app.app_context():
        deleted = SupportSeekerProfile.query.get(p_id)
        assert deleted is None

def test_api_health_endpoint(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'healthy'
    assert data['database_connected'] is True
    assert 'Udaan AI' in data['service']

def test_api_impact_stats(client, seeded_data):
    res = client.get('/api/impact-stats')
    assert res.status_code == 200
    data = res.get_json()
    assert 'total_profiles' in data
    assert 'category_distribution' in data
    assert 'referral_distribution' in data
