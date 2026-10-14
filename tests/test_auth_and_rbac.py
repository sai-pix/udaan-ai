from app.models.user import User

def test_password_hashing(app, seeded_data):
    with app.app_context():
        user = User.query.get(seeded_data['admin_u_id'])
        assert user.check_password("AdminPass123!") is True
        assert user.check_password("WrongPassword") is False

def test_login_success(client, seeded_data):
    res = client.post('/login', data={
        'identifier': 'test_admin',
        'password': 'AdminPass123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome back, test_admin!" in res.data

def test_login_invalid_credentials(client, seeded_data):
    res = client.post('/login', data={
        'identifier': 'test_admin',
        'password': 'WrongPassword!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Invalid username/email or password" in res.data

def test_rbac_admin_protected(client, seeded_data):
    # Anonymous request to admin dashboard should redirect to login
    res = client.get('/admin/dashboard', follow_redirects=True)
    assert b"Please sign in to access this portal" in res.data or b"Please sign in" in res.data

    # Log in as seeker and attempt admin access -> Access denied
    client.post('/login', data={'identifier': 'seeker_1', 'password': 'SeekerPass123!'})
    res = client.get('/admin/dashboard', follow_redirects=True)
    assert b"Access denied: You do not have permissions" in res.data

    # Log in as admin -> Success
    client.get('/logout')
    client.post('/login', data={'identifier': 'test_admin', 'password': 'AdminPass123!'})
    res = client.get('/admin/dashboard')
    assert res.status_code == 200
    assert b"Platform Overview" in res.data

def test_bootstrap_admin(client):
    res = client.post('/bootstrap-admin', data={
        'setup_secret': 'TestBootstrapSecret123!',
        'username': 'new_bootstrap_admin',
        'email': 'boot@udaan.org',
        'password': 'BootstrapPass2026!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Administrator account successfully bootstrapped" in res.data
