import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, login_manager
from routes import main_bp
from models import User

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///health_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()
        
        # Seed Super Admin
        if not User.query.filter_by(username='adminsuper').first():
            print("Seeding Super Admin account...")
            super_admin = User(username='adminsuper', role='admin_iii')
            super_admin.set_password('adminsuper321')
            db.session.add(super_admin)
            db.session.commit()
            print("Super Admin created.")
        
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
