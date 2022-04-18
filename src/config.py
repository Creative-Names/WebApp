class Config(object):

    SECRET_KEY = 'tHiSiSnOtAsEcReTkEy'

    SQLALCHEMY_BINDS = {
        'user_db': 'sqlite:///data/users.db',
        'post_db': 'sqlite:///data/post.db',
        'dm_db': 'sqlite:///data/dm.db'
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SERVER_NAME = 'creativecorner.app.vtxhub.com'
    SERVER_NAME = 'localhost:9422'

    HTTP_STATUS = 'http://'