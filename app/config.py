import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')

    BREVO_API_KEY = os.environ.get('BREVO_API_KEY')

    MAIL_SENDER_EMAIL = os.environ.get(
        'MAIL_SENDER_EMAIL'
    )

    MAIL_SENDER_NAME = os.environ.get(
        'MAIL_SENDER_NAME',
        'LifePATH',
    )

    R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
    R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')

    R2_SECRET_ACCESS_KEY = os.environ.get(
        'R2_SECRET_ACCESS_KEY'
    )

    R2_BUCKET_NAME = os.environ.get(
        'R2_BUCKET_NAME',
        'lifepath-releases',
    )

    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024