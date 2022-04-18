from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy




db = SQLAlchemy()


class User(UserMixin, db.Model):

    __bind_key__ = 'user_db'

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(), unique=True)
    password = db.Column(db.String(), nullable=False)
    username = db.Column(db.String(), nullable=False)
    about = db.Column(db.String())
    date_joined = db.Column(db.String(), nullable=False)
    relations = db.Column(db.String())
    role = db.Column(db.String(), nullable=False)
    

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email

    def __repr__(self):
        return f"{self.id} - {self.username} - {self.email} - {self.role}"




class Post(db.Model):

    __bind_key__ = 'post_db'
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.String(), nullable=False)
    poster = db.Column(db.String(), nullable=False)

    likes = db.Column(db.String())
    timestamp = db.Column(db.String(), nullable=False)
    replies = db.Column(db.String())

    def __repr__(self):
        return f"{self.content} - {self.poster}"



class DM(db.Model):
    __bind_key__ = 'dm_db'
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.String(), nullable=False)
    _from = db.Column(db.String(), nullable=False)
    _to = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"{self._from} -> {self._to} - {self.content}"



