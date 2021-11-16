from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import api
import config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    Migrate().init_app(app, db)

    app.register_blueprint(api.bp)

    

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
