import os
from flask import Flask
from flask_smorest import Api
from flask_migrate import Migrate
from datetime import timedelta
from dotenv import load_dotenv

from db import db
import models

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

from jwt_manager import register_jwt_manager


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)

    register_jwt_manager(app)

    db.init_app(app)

    '''
        flask migrate automatically creates table,
        so we no longer need SQLAlchemy to do it.

        Run "flask db init" (added by flask migrate) on terminal.

        It will create a migrations folder.

        Run "flask db migrate" to create a migration.

            * It'll compare the existing database with the
              database defined by the models. Then, it creates
              a script that allows to go from one version to
              the other.

            **If there's not database set up yet, it'll create
              one based on our models.

        To apply migration, run "flask db upgrade". The latest
        migration will be applied.
    '''
    migrate = Migrate(app, db)

    #with app.app_context():
        #db.create_all()

    api = Api(app)

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
