from flask import Flask
from models import User, Post, DM
from app import db
app = Flask(__name__, subdomain_matching=True)
app.config.from_object('config.Config')
db.init_app(app)
with app.app_context():
   db.create_all()
