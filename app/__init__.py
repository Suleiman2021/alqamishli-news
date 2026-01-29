from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
from app.config import Config

import geoip2.database
import os

db = SQLAlchemy()
mail = Mail()




# تحديد المسار للملف
GEOIP_DB_PATH = os.path.join("app", "static", "dbip-country-lite-2026-01.mmdb")

# إنشاء قارئ قاعدة البيانات
geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)

def get_country_from_ip(ip):
    try:
        # تجاهل IP المحلي
        if ip in ("127.0.0.1", "localhost"):
            return "محلي"

        response = geoip_reader.country(ip)
        return response.country.name or "غير معروف"

    except Exception:
        return "غير معروف"




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
        
        # تجاهل الأدمن
        if request.path.startswith("/admin"):
            return

        # تجاهل favicon و health checks
        if request.path in ["/favicon.ico"] or request.method == "HEAD":
            return

        forwarded_for = request.headers.get("X-Forwarded-For")

        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.remote_addr


        path = request.path

        visitor = Visitor.query.filter_by(ip_address=ip).first()

        if visitor:
            visitor.visits_count += 1
            visitor.last_visit = datetime.utcnow()
        else:
            country = get_country_from_ip(ip)

            visitor = Visitor(
                ip_address=ip,
                country=country
            )

            db.session.add(visitor)
            db.session.flush()  # للحصول على ID مباشرة

        page = VisitedPage(
            visitor_id=visitor.id,
            path=path
        )

        db.session.add(page)
        db.session.commit()

    return app
