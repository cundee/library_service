from flask import Flask
from database import db
from flask_migrate import Migrate
from models.model import *
import api
import config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    Migrate().init_app(app, db)

    app.register_blueprint(api.bp)
    app.secret_key = "SUPER SECRET KEY"
    

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
