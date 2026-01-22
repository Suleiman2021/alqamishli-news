from flask import Blueprint, render_template, redirect, url_for
from app.models import News, Bookmark, BreakingNews
from app import db

bookmarks = Blueprint("bookmarks", __name__)


@bookmarks.route("/bookmarks")
def bookmarks_page():
    breaking_news = (
        BreakingNews.query
        .filter_by(is_active=True)
        .order_by(BreakingNews.created_at.desc())
        .all()
    )       
    bookmarks_list = Bookmark.query.order_by(Bookmark.created_at.desc()).all()
    return render_template(
        "frontend/bookmarks.html",
        bookmarks=bookmarks_list,   # ← هنا أرسل اسم المتغير الذي سيستخدمه القالب
        breaking_news=breaking_news
    )


@bookmarks.route("/bookmark/<int:news_id>")
def add_bookmark(news_id):
    exists = Bookmark.query.filter_by(news_id=news_id).first()
    if not exists:
        db.session.add(Bookmark(news_id=news_id))
        db.session.commit()
    return redirect(url_for("bookmarks.bookmarks_page"))

@bookmarks.route("/bookmark/<int:id>/delete", methods=["POST"])
def delete_bookmark(id):
    bookmark = Bookmark.query.get_or_404(id)
    db.session.delete(bookmark)
    db.session.commit()
    return redirect(url_for("bookmarks.bookmarks_page"))
