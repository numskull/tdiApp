import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    BASE_DIR = basedir
    STATIC_DIR = os.path.join(basedir, '\app\static')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass

class developmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    BASE_DIR = basedir
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' \
                              + os.path.join(basedir, 'data-test.sqlite')

config = {
    'development': developmentConfig,
    'default': developmentConfig
}