from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
from extensions import configure_extensions, db

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config.update({
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-key-123'),
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///wayne_security.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif'},
        'UPLOAD_FOLDER': os.path.join('routes', 'temp_uploads'),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024  # 16MB
    })
   
    # Inicializar banco de dados
    db.init_app(app)

    # Inicializar LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Definir user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Registrar blueprints e criar tabelas
    with app.app_context():
        from models import User, Item
        from routes.auth import bp as auth_bp
        from routes.dashboard import dashboard_bp
        
        db.create_all()
        
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)