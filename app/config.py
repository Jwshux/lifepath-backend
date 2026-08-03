import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_APP_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

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