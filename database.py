from main import app
from models import db, User, IOC

with app.app_context():
    # Yeni user əlavə et
    user = User(username='admin', password='123456')
    db.session.add(user)
    db.session.commit()

    # Yeni IOC əlavə et
    ioc = IOC(value='malicious.com', type='domain', user_id=user.id)
    db.session.add(ioc)
    db.session.commit()

    # Verilənləri göstər
    print(User.query.all())
    print(IOC.query.all())
