from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
from app.config import Config

db = SQLAlchemy()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    # ----------------- Blueprints -----------------
    from app.routes import main
    app.register_blueprint(main, url_prefix="/admin")

    from app.routes_public import public
    app.register_blueprint(public)

    from app.routes_bookmarks import bookmarks
    app.register_blueprint(bookmarks)

    # ----------------- Visitor Tracking -----------------
    from app.models import Visitor, VisitedPage

    @app.before_request
    def track_visits():
        # تجاهل الملفات الثابتة
        if request.path.startswith("/static"):
            return

        # تجاهل favicon و health checks
        if request.path in ["/favicon.ico"] or request.method == "HEAD":
            return

        ip = request.headers.get(
            "X-Forwarded-For",
            request.remote_addr
        )

        path = request.path

        visitor = Visitor.query.filter_by(ip_address=ip).first()

        if visitor:
            visitor.visits_count += 1
            visitor.last_visit = datetime.utcnow()
        else:
            visitor = Visitor(ip_address=ip)
            db.session.add(visitor)
            db.session.flush()  # للحصول على ID مباشرة

        page = VisitedPage(
            visitor_id=visitor.id,
            path=path
        )

        db.session.add(page)
        db.session.commit()

    return app
