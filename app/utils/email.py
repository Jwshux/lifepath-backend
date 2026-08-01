from flask_mail import Message

from ..extensions import mail


def send_account_recovery_email(
    recipient_email,
    username,
    reset_code,
):
    message = Message(
        subject='LifePATH Account Recovery',
        recipients=[recipient_email],
    )

    message.body = f"""Hello {username},

Someone requested account recovery for your LifePATH account.

Account Username
{username}

Verification Code
{reset_code}

This verification code expires in 10 minutes.

For your security:
• Never share this verification code with anyone.
• LifePATH will never ask you for this code.
• If you didn't make this request, you can safely ignore this email.

Thank you,

The LifePATH Team
"""

    mail.send(message)