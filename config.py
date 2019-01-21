import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    WTF_CSRF_ENABLED = False
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, "db_repository")

    # This allows the application to customize the configuration.
    # Add appropriate code if want to implement some app level customization
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE =  "sqlite" # {"mysql", "sqlite"} used for date conversions
    EXPLAIN_TEMPLATE_LOADING = True
    DATABASE_FILE_1 = "chinook.sqlite"
    DATABASE_FILE_2 = "pab.sqlite"

    # SQLALCHEMY_DATABASE_URI is the default connection used if no bind key = None (no bind key is specified in the model)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, DATABASE_FILE_1)

    # see http://flask-sqlalchemy.pocoo.org/2.3/binds/
    SQLALCHEMY_BINDS = {
        "models_pab":"sqlite:///" + os.path.join(basedir, DATABASE_FILE_2)
    }

    # list database(s) that are shown on scrudadmin page -- select by bind key
    # provides mapping from models.py file to database name
    # sqlalchemy convention default db bind=None
    SCRUD_BINDS = {None:DATABASE_FILE_1,
                   "models_pab":DATABASE_FILE_2}


class ProductionConfig(Config):
    DEBUG = False
    DATABASE =  "sqlite" # {"mysql", "sqlite"} used for date conversions
    EXPLAIN_TEMPLATE_LOADING = True
    DATABASE_FILE_1 = "chinook.sqlite"
    DATABASE_FILE_2 = "pab.sqlite"

    # SQLALCHEMY_DATABASE_URI is the default connection used if no bind key = None (no bind key is specified in the model)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, DATABASE_FILE_1)

    # see http://flask-sqlalchemy.pocoo.org/2.3/binds/
    SQLALCHEMY_BINDS = {
        "models_pab":"sqlite:///" + os.path.join(basedir, DATABASE_FILE_2)
    }

    # list database(s) that are shown on scrudadmin page -- select by bind key
    # provides mapping from models.py file to database name
    # sqlalchemy convention default db bind=None
    SCRUD_BINDS = {None:DATABASE_FILE_1,
                   "models_pab":DATABASE_FILE_2}

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

# Set this to config["key"].  It sets the configuration in app/__init__.py
conf = config["development"]
