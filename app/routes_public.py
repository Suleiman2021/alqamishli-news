# app/routes_public.py
from flask import render_template, request, redirect, url_for, flash
from app.models import ContactMessage, BreakingNews
from app.models import About
from app import db
from flask import Blueprint, render_template, request
from app.models import News
import re
from sqlalchemy import or_

public = Blueprint("public", __name__)

# ======================
# الصفحة الرئيسية
# ======================
@public.route("/")
def index():
    breaking_news = (
        BreakingNews.query
        .filter_by(is_active=True)
        .order_by(BreakingNews.created_at.desc())
        .all()
    )     
    news_list = News.query.order_by(News.created_at.desc()).all()
    featured_news = News.query.filter_by(is_featured=True).limit(3).all()

    return render_template(
        "frontend/index.html",
        news_list=news_list,
        featured_news=featured_news,
        breaking_news=breaking_news
    )


# ======================
# صفحة الفئات
# ======================
@public.route("/category/<category>")
def category(category):
    breaking_news = (
        BreakingNews.query
        .filter_by(is_active=True)
        .order_by(BreakingNews.created_at.desc())
        .all()
    )     
    news_list = (
        News.query
        .filter_by(category=category)
        .order_by(News.created_at.desc())
        .all()
    )

    return render_template(
        "frontend/category.html",
        category=category,
        news_list=news_list,
        breaking_news=breaking_news
    )


# ======================
# صفحة تفاصيل الخبر
# ======================
@public.route("/news/<slug>")
def news_detail(slug):

    breaking_news = (
        BreakingNews.query
        .filter_by(is_active=True)
        .order_by(BreakingNews.created_at.desc())
        .all()
    )       
    news = News.query.filter_by(slug=slug).first_or_404()

    # أخبار ذات صلة (نفس الفئة – باستثناء الخبر الحالي)
    related_news = (
        News.query
        .filter(News.category == news.category, News.id != news.id)
        .limit(5)
        .all()
    )

    return render_template(
        "frontend/article.html",
        news=news,
        related_news=related_news,
        breaking_news=breaking_news
    )


# ======================
# صفحة البحث
# ======================
@public.route("/search")
def search():
    breaking_news = (
        BreakingNews.query
        .filter_by(is_active=True)
        .order_by(BreakingNews.created_at.desc())
        .all()
    )   
    
    q = request.args.get("q", "")

    

    news_list = []
    if q:
        q = q.strip()

        news_list = (
            News.query
            .filter(
                or_(
                    News.title.ilike(f"%{q}%"),
                    News.content.ilike(f"%{q}%"),
                    News.meta_description.ilike(f"%{q}%")
                )
            )
            .order_by(News.created_at.desc())
            .all()
        )


    return render_template(
        "frontend/search.html",
        query=q,
        news_list=news_list,
        breaking_news=breaking_news
    )





# ======================
# من نحن
# ======================


@public.route("/about")
def about():
    breaking_news = (
        BreakingNews.query
        .filter_by(is_active=True)
        .order_by(BreakingNews.created_at.desc())
        .all()
    )

    about = About.query.first()

    return render_template(
        "frontend/about.html",
        about=about,
        breaking_news=breaking_news
    )


# ======================
# اتصل بنا
# ======================

@public.route("/contact", methods=["GET", "POST"])
def contact():

    breaking_news = (
        BreakingNews.query
        .filter_by(is_active=True)
        .order_by(BreakingNews.created_at.desc())
        .all()
    )


    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]
        

        msg = ContactMessage(
            name=name,
            email=email,
            message=message
        )

        email = email.strip()

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash("❌ يرجى إدخال بريد إلكتروني صحيح")
            return redirect(url_for("public.contact"))

        db.session.add(msg)
        db.session.commit()

        flash("تم إرسال رسالتك بنجاح ✔", "success")
        return redirect(url_for("public.contact"))

    return render_template(
        "frontend/contact.html",
        breaking_news=breaking_news
    )





