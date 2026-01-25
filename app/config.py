import os

class Config:
    # --------------------
    # Security
    # --------------------
    SECRET_KEY = os.getenv("SECRET_KEY")

    # --------------------
    # Database
    # --------------------
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --------------------
    # Mail (Flask-Mail)
    # --------------------
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))

    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_SENDER_NAME", "slslkennews"),
        os.getenv("MAIL_USERNAME"),
    )

    # ⏱️ مهم جدًا لمنع Gunicorn timeout
    MAIL_TIMEOUT = 10
