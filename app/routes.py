# app/routes.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app.models import Admin, News, BreakingNews, ContactMessage
from app import db
import re
from flask_mail import Message
from app import mail

from cloudinary.uploader import upload

from flask import jsonify
from datetime import datetime

# from app.models import ContactMessage
# from flask import request, flash

# main = Blueprint("main", __name__)
main = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)



@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            session["admin_logged_in"] = True
            session["admin_id"] = admin.id
            return redirect(url_for("admin.news_list"))
        else:
            flash("❌ بيانات الدخول غير صحيحة", "error")

    return render_template("login.html")



@main.route("/settings", methods=["GET", "POST"])
def settings():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    admin = Admin.query.get(session["admin_id"])

    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not all([old_password, new_password, confirm_password]):
            flash("❌ يرجى ملء جميع الحقول", "error")
            return redirect(url_for("admin.settings"))

        if not check_password_hash(admin.password_hash, old_password):
            flash("❌ كلمة المرور الحالية غير صحيحة", "error")
            return redirect(url_for("admin.settings"))

        if len(new_password) < 6:
            flash("❌ كلمة المرور الجديدة قصيرة جداً", "error")
            return redirect(url_for("admin.settings"))

        if new_password != confirm_password:
            flash("❌ كلمتا المرور غير متطابقتين", "error")
            return redirect(url_for("admin.settings"))

        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash("✅ تم تغيير كلمة المرور بنجاح", "success")
        return redirect(url_for("admin.settings"))

    return render_template("settings.html")


@main.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("admin.login"))




# -------------- news-form --------------



UPLOAD_FOLDER = "app/static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}



@main.route("/upload-image", methods=["POST"])
def upload_image():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    filename = secure_filename(file.filename)

    # لتجنب تكرار الأسماء
    name, ext = os.path.splitext(filename)
    filename = f"{name}_{int(datetime.now().timestamp())}{ext}"

    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    # 🔑 مهم جدًا: إعادة رابط داخل static
    return jsonify({
        "location": url_for("static", filename=f"uploads/{filename}")
    })





def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

@main.route("/news/<int:id>/edit", methods=["GET", "POST"])
@main.route("/news/new", methods=["GET", "POST"])
def news_form(id=None):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    news = News.query.get(id) if id else None

    if request.method == "POST":
        title = request.form.get("title")
        slug = request.form.get("slug") or title.replace(" ", "-")
        meta_description = request.form.get("meta_description")
        category = request.form.get("category")
        content = request.form.get("content")
        image_url = request.form.get("image_url")
        
        image_url = request.form.get("image_url")
        image_file = request.files.get("image_file")

        if image_file and image_file.filename != "":
            result = upload(image_file)
            image_url = result["secure_url"]


        is_featured = True if request.form.get("is_featured") == "on" else False

        # ✅ تحقق من رابط الصورة
        if image_url and not image_url.startswith("http"):
            flash("❌ يجب إدخال رابط صورة كامل يبدأ بـ http أو https", "error")
            return redirect(request.url)

        if image_url and image_url.startswith("data:"):
            flash("❌ لا يسمح بروابط Base64 للصور", "error")
            return redirect(request.url)

        if not title or not content:
            flash("❌ العنوان والمحتوى مطلوبان", "error")
            return redirect(request.url)

        if news:
            news.title = title
            news.slug = slug
            news.meta_description = meta_description
            news.category = category
            news.content = content
            news.image_url = image_url
            news.is_featured = is_featured
            news.image_url = image_url
            # news.image_file = image_filename if image_filename else news.image_file

        else:
            news = News(
                title=title,
                slug=slug,
                meta_description=meta_description,
                category=category,
                content=content,
                image_url=image_url,
                # image_file=image_filename,
                is_featured=is_featured
            )
            db.session.add(news)

        db.session.commit()
        flash("✅ تم حفظ الخبر بنجاح", "success")
        return redirect(url_for("admin.news_list"))

    return render_template("news-form.html", news=news)




# ----------------- news ----------------------

@main.route("/news")
def news_list():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

# جلب جميع الاخبار من قاعدة البيانات 
    news_list = News.query.order_by(News.created_at.desc()).all()
    return render_template("news.html", news_list=news_list)


@main.route("/news/<int:id>/delete", methods=["POST"])
def delete_news(id):
    news = News.query.get_or_404(id)
    db.session.delete(news)
    db.session.commit()
    flash("✅ تم حذف الخبر بنجاح", "success")
    return redirect(url_for("admin.news_list"))







# ----------------- Breaking News ----------------------

@main.route("/breaking-news", methods=["GET", "POST"])
def breaking_news():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    if request.method == "POST":
        content = request.form.get("content")

        if not content:
            flash("❌ نص الخبر العاجل مطلوب", "error")
            return redirect(url_for("admin.breaking_news"))

        # تعطيل كل الأخبار السابقة
        BreakingNews.query.update({BreakingNews.is_active: False})

        # إضافة خبر جديد
        news = BreakingNews(content=content, is_active=True)
        db.session.add(news)
        db.session.commit()

        flash("✅ تم إضافة الخبر العاجل", "success")
        return redirect(url_for("admin.breaking_news"))

    breaking_list = BreakingNews.query.order_by(BreakingNews.created_at.desc()).all()
    return render_template("breaking-news.html", breaking_list=breaking_list)


@main.route("/breaking-news/<int:id>/delete", methods=["POST"])
def delete_breaking_news(id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    news = BreakingNews.query.get_or_404(id)
    db.session.delete(news)
    db.session.commit()

    flash("🗑️ تم حذف الخبر العاجل", "success")
    return redirect(url_for("admin.breaking_news"))




@main.route("/breaking-news/<int:id>/toggle", methods=["POST"])
def toggle_breaking_news(id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    news = BreakingNews.query.get_or_404(id)

    # # إذا فعلناه -> عطّل كل غيره
    # if not news.is_active:
    #     BreakingNews.query.update({BreakingNews.is_active: False})

    news.is_active = not news.is_active
    db.session.commit()

    flash("✅ تم تحديث حالة الخبر", "success")
    return redirect(url_for("admin.breaking_news"))






@main.route("/contact-messages")
def contact_messages():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("contact-messages.html", messages=messages)







# ------------------------------------------

@main.route("/contact-messages/<int:id>/reply", methods=["GET", "POST"])
def reply_message(id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    message = ContactMessage.query.get_or_404(id)

    

    email_to = message.email.strip()
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if not re.match(email_regex, email_to):
        flash("❌ البريد الإلكتروني غير صالح، لا يمكن إرسال الرد", "error")
        return redirect(url_for("admin.contact_messages"))


    if request.method == "POST":
        reply_text = request.form.get("reply")

        if not reply_text:
            flash("❌ يجب كتابة الرد", "error")
            return redirect(request.url)

        # 📧 إنشاء البريد
        email = Message(
            subject="الرد على رسالتك - slslkennews",
            recipients=[email_to],
            body=f"""
مرحبًا {message.name},

شكرًا لتواصلك معنا.

ردنا على رسالتك:
-----------------------
{reply_text}

مع التحية،
فريق slslkennews
"""
        )

        try:
            mail.send(email)
            message.is_read = True
            db.session.commit()
            flash("✅ تم إرسال الرد بنجاح", "success")
        except Exception as e:
            flash("❌ فشل إرسال البريد", "error")

        return redirect(url_for("admin.contact_messages"))

    return render_template("reply-message.html", message=message)
