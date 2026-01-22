from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from app.config import Config

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    # Admin backend
    from app.routes import main
    app.register_blueprint(main, url_prefix='/admin')

    # Public frontend
    from app.routes_public import public
    app.register_blueprint(public)

    from app.routes_bookmarks import bookmarks
    app.register_blueprint(bookmarks)

    return app
