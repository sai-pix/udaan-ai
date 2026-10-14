from app.models.seeker_profile import SupportSeekerProfile
from app.models.referral import ReferralRequest
from app.services.referral_service import ReferralService
from app.extensions import db

def test_referral_creation_and_ref_code(app, seeded_data):
    with app.app_context():
        profile = SupportSeekerProfile(
            alias_name="Anand M.",
            contact_phone="+91 99999 88888",
            city="Visakhapatnam",
            skills=["Warehouse"],
            consent_given=True
        )
        db.session.add(profile)
        db.session.commit()

        referral = ReferralService.create_referral(
            profile_id=profile.id,
            organization_id=seeded_data['org_a_id'],
            alias_name=profile.alias_name,
            phone=profile.contact_phone
        )

        assert referral.reference_number.startswith("REF-2026-")
        assert referral.status == "submitted"
        assert referral.consented_data_snapshot['alias_name'] == "Anand M."
        assert len(referral.followups) > 0

def test_organization_data_isolation(client, app, seeded_data):
    with app.app_context():
        profile = SupportSeekerProfile(alias_name="Isolation Tester", city="Visakhapatnam", consent_given=True)
        db.session.add(profile)
        db.session.commit()

        # Referral created specifically for Org B (Deccan Agri)
        ref_b = ReferralService.create_referral(
            profile_id=profile.id,
            organization_id=seeded_data['org_b_id'],
            alias_name="Seeker For Org B"
        )
        ref_b_id = ref_b.id

    # Log in as Staff from Org A (Karuna Shelter Trust)
    client.post('/login', data={'identifier': 'ngo_staff_a', 'password': 'NgoPass123!'})

    # Attempt to view Referral assigned to Org B -> MUST BE FORBIDDEN (403)
    res = client.get(f'/org/referral/{ref_b_id}')
    assert res.status_code == 403

    # Attempt to POST status update to Referral assigned to Org B -> MUST BE FORBIDDEN (403)
    res_update = client.post(f'/org/referral/{ref_b_id}', data={'status': 'accepted'})
    assert res_update.status_code == 403

def test_referral_status_lifecycle_updates(client, app, seeded_data):
    with app.app_context():
        profile = SupportSeekerProfile(alias_name="Lifecycle Tester", city="Visakhapatnam", consent_given=True)
        db.session.add(profile)
        db.session.commit()

        # Referral for Org A
        ref_a = ReferralService.create_referral(
            profile_id=profile.id,
            organization_id=seeded_data['org_a_id'],
            alias_name="Lifecycle Seeker"
        )
        ref_a_id = ref_a.id

    # Log in as Staff from Org A
    client.post('/login', data={'identifier': 'ngo_staff_a', 'password': 'NgoPass123!'})

    # Staff A updates status to 'accepted' with caseworker notes
    res = client.post(f'/org/referral/{ref_a_id}', data={
        'status': 'accepted',
        'staff_notes': 'Candidate confirmed for preliminary intake.'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"updated to" in res.data and b"accepted" in res.data

    with app.app_context():
        ref = ReferralRequest.query.get(ref_a_id)
        assert ref.status == 'accepted'
        assert ref.staff_notes == 'Candidate confirmed for preliminary intake.'
        # Check follow-up record created
        assert any(fu.milestone == 'appointment_confirmed' for fu in ref.followups)

def test_public_referral_tracking_no_login_needed(client, app, seeded_data):
    with app.app_context():
        profile = SupportSeekerProfile(alias_name="Public Tracker", city="Visakhapatnam", consent_given=True)
        db.session.add(profile)
        db.session.commit()

        ref = ReferralService.create_referral(
            profile_id=profile.id,
            organization_id=seeded_data['org_a_id'],
            alias_name="Public Tracker"
        )
        ref_num = ref.reference_number

    # Public user queries without logging in
    res = client.get(f'/referral/track?ref={ref_num}')
    assert res.status_code == 200
    assert ref_num.encode() in res.data
    assert b"Referred Organization" in res.data
