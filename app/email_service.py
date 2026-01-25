import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to, subject, html):
    resend.Emails.send({
        "from": "Al-Qamishli News <onboarding@resend.dev>",
        "to": [to],
        "subject": subject,
        "html": html
    })
