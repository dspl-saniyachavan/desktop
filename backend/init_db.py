import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.user import User
from app.models.parameter import Parameter

app = create_app()

with app.app_context():
    db.create_all()
    
    existing_user = User.query.filter_by(email='admin@precisionpulse.com').first()
    if not existing_user:
        user = User(email='admin@precisionpulse.com', name='Admin User', role='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        print("✓ Admin user created: admin@precisionpulse.com / admin123")
    else:
        print("✓ Admin user already exists")
    
    client_user = User.query.filter_by(email='client@precisionpulse.com').first()
    if not client_user:
        user = User(email='client@precisionpulse.com', name='Client User', role='client')
        user.set_password('client123')
        db.session.add(user)
        db.session.commit()
        print("✓ Client user created: client@precisionpulse.com / client123")
    else:
        print("✓ Client user already exists")
    
    default_params = [
        ('Temperature', '°C', 'Ambient temperature sensor'),
        ('Pressure', 'kPa', 'System pressure measurement'),
        ('Flow Rate', 'L/s', 'Liquid flow rate'),
        ('Humidity', '%', 'Relative humidity'),
        ('Voltage', 'V', 'System voltage'),
        ('Current', 'A', 'System current'),
    ]
    
    for name, unit, description in default_params:
        existing = Parameter.query.filter_by(name=name).first()
        if not existing:
            param = Parameter(name=name, unit=unit, description=description, enabled=True, is_default=True)
            db.session.add(param)
    
    db.session.commit()
    print("✓ Default parameters created")
