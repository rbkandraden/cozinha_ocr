from flask import Flask
from flask_login import LoginManager
import os
from models import db, User, bcrypt  # Agora não causa import circular

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wayne_security.db'

# Agora inicializamos as extensões corretamente
db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Importação e registro dos blueprints (somente agora, após criar app)
from routes.auth import bp as auth_bp
from routes.dashboard import bp as dashboard_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria o banco de dados sem erro
    app.run(debug=True)