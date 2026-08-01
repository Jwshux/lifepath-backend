from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from pymongo import MongoClient

bcrypt = Bcrypt()
cors = CORS()
mail = Mail()

mongo_client = None
db = None


def init_mongo(app):
    global mongo_client, db

    mongo_client = MongoClient(app.config['MONGO_URI'])
    db = mongo_client.get_database('lifepath')

    return db