import os
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    # Ensure database tables exist
    db.create_all()
    # Check if database is empty; if so, run demo seeder
    from app.models.organization import Organization
    if Organization.query.count() == 0 and os.environ.get('DEMO_MODE', 'true').lower() in ('true', '1', 'yes'):
        from scripts.seed_demo import seed_database
        try:
            seed_database()
        except Exception as e:
            print(f"Initial seed warning: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() in ('true', '1')
    app.run(host='0.0.0.0', port=port, debug=debug)
