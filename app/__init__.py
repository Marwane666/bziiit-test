from flask import Flask
from flask_wtf import CSRFProtect

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    csrf = CSRFProtect(app)
    csrf.init_app(app)

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app