from app.services.i18n_service import t, PRACTICAL_BARRIERS, SUPPORT_CATEGORIES

def test_i18n_service_english():
    assert t('app_name', lang='en') == 'Udaan AI'
    assert 'Barrier-Aware' in t('hero_title', lang='en')
    assert 'Personalized Pathway Intake' in t('intake_title', lang='en')

def test_i18n_service_telugu():
    assert 'ఉడాన్' in t('app_name', lang='te')
    assert 'జీవనోపాధి' in t('hero_title', lang='te')
    assert 'నమోదు' in t('intake_title', lang='te')

def test_i18n_service_fallback():
    assert t('non_existent_key_xyz', lang='en', default='Fallback Text') == 'Fallback Text'

def test_barriers_and_categories_have_telugu():
    for b in PRACTICAL_BARRIERS:
        assert 'label_en' in b
        assert 'label_te' in b
        assert len(b['label_te']) > 0

    for s in SUPPORT_CATEGORIES:
        assert 'label_en' in s
        assert 'label_te' in s
        assert len(s['label_te']) > 0

def test_language_toggle_route(client):
    res = client.get('/set-language/te', follow_redirects=True)
    assert res.status_code == 200
    with client.session_transaction() as sess:
        assert sess['lang'] == 'te'

    res = client.get('/set-language/en', follow_redirects=True)
    assert res.status_code == 200
    with client.session_transaction() as sess:
        assert sess['lang'] == 'en'
