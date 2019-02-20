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
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgres://mapyqqxxdlebuf:b0e059c94bedf2d345829ab4ef236d43d3641efb6da961e25a927561b54092c0@ec2-54-83-44-4.compute-1.amazonaws.com:5432/d1hk326n4v5lm9herok') or 'sqlite:///' \
                              + os.path.join(basedir, 'data-test.sqlite')

config = {
    'development': developmentConfig,
    'default': developmentConfig
}