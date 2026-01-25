import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to, subject, html):
    resend.Emails.send({
        "from": "Al-Qamishli News <no-reply@alqamishli-news.onrender.com>",
        "to": [to],
        "subject": subject,
        "html": html
    })
