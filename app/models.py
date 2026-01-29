from app import db
from datetime import datetime


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)

class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    meta_description = db.Column(db.String(160))
    image_url = db.Column(db.String(255))  # ← استخدم هذا بدلاً من "image"
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    is_featured = db.Column(db.Boolean, default=False)
    image_file = db.Column(db.String(255))

    bookmarks = db.relationship(
        "Bookmark",
        backref="news",
        cascade="all, delete-orphan",
        passive_deletes=True
        )


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'  # تأكد من الاسم مطابق للجدول
    id = db.Column(db.Integer, primary_key=True)
    
    news_id = db.Column(
    db.Integer,
    db.ForeignKey("news.id", ondelete="CASCADE"),
    nullable=False
    )

    created_at = db.Column(db.DateTime, default=db.func.now())

    # news = db.relationship('News', backref='bookmarked')


class BreakingNews(db.Model):
    __tablename__ = "breaking_news"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    is_read = db.Column(db.Boolean, default=False)



class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), index=True)
    country = db.Column(db.String(100))  # 🟢 الدولة
    visits_count = db.Column(db.Integer, default=1)
    last_visit = db.Column(db.DateTime, default=datetime.utcnow)

    pages = db.relationship("VisitedPage", backref="visitor", lazy=True)


class VisitedPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey("visitor.id"))
    path = db.Column(db.String(255))
    visited_at = db.Column(db.DateTime, default=datetime.utcnow)





class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)