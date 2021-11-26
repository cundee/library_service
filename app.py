from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import api
import config
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    Migrate().init_app(app, db)

    app.register_blueprint(api.bp)
    app.secret_key = os.environ.get('SECRET_KEY')
    

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
