from flask import Flask
from models import *

app = Flask(__name__)
def setup_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///db.sqlite3"
    db.init_app(app)
    #Pending here is sqlite
    app.app_context().push()  #direct access to other modules
    app.debug= True
    print("Started ....")

setup_app()    

from routes import *

if __name__ == '__main__':
    db.create_all()
    admin_user = User.query.filter_by(email='admin@gmail.com').first()
    if not admin_user:
        admin = User(
            email='admin@gmail.com',
            password='admin@123',
            name='Admin',
            address='Delhi',
            pincode=110078,
            role=0
        )
        db.session.add(admin)
        db.session.commit()

    app.run(debug=True)
