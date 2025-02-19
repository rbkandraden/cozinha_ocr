from flask import Flask, redirect, url_for
from flask_login import LoginManager
import os
from models import db, User, bcrypt  

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wayne_security.db'


db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from routes.auth import bp as auth_bp
from routes.dashboard import bp as dashboard_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

@app.route("/")
def index():
    return redirect(url_for("auth.login"))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
