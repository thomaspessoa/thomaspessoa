import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
login_manager.login_message = "Por favor, faça login para acessar esta página."


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'  # Change this!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['UPLOAD_FOLDER'] = 'static/product_pics'

    db.init_app(app)
    login_manager.init_app(app)

    from marketplace.routes import main
    app.register_blueprint(main)

    with app.app_context():
        os.makedirs(os.path.join(app.root_path, 'static', 'product_pics'), exist_ok=True)

    return app
