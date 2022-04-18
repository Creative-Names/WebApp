from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user
from models import User, DM, Post #type: ignore
from models import db #type: ignore
from flask_cors import CORS
from flask_socketio import SocketIO #type: ignore
from threading import RLock
import datetime

from employerApp.employer import employer_bp #type: ignore
from customerApp.customers import customer_bp #type: ignore

app = Flask(__name__, subdomain_matching=True)
app.config.from_object('config.Config')
CORS(app)

lock = RLock()

db.init_app(app)
socketio = SocketIO(app)

ids = {}



login = LoginManager()
login.init_app(app)

app.register_blueprint(employer_bp, subdomain='employer')

app.register_blueprint(customer_bp, subdomain='explore')


http_status = app.config['HTTP_STATUS']
hostname = app.config['SERVER_NAME']

login.blueprint_login_views = {
    'shopkeeper_bp': f"{http_status}employer.{hostname}/login",
    'customer_bp': f"{http_status}explore.{hostname}/login"
}

@login.user_loader
def load_user(email):
    account = User.query.filter_by(email=email).first()
    return account


@app.context_processor
def inject_details():
    return dict(http_status = app.config['HTTP_STATUS'], hostname = app.config['SERVER_NAME'], LoggedIn = current_user.is_authenticated, current_user=current_user)


@app.route('/', strict_slashes=False)
def main():
    global ids
    return render_template("index.html")

@app.route('/faq', strict_slashes=False)
def faq():
    return render_template("about.html")

@app.route('/search', strict_slashes=False)
def search():
    try:
        query = request.args['query']
    except KeyError:
        return redirect(url_for('main'))
    if query == "":
        return redirect(url_for('main'))
    
    s_posts = Post.query.filter(Post.content.contains(query)).all()
    
    for post in s_posts:
        name = User.query.filter_by(email=post.poster).first()
        post.name = name.username
    
    
    return render_template("search.html", posts=s_posts)
    


@socketio.on('connect')
def connect():
    print('connected')

    
@socketio.on('id')
def storeID(*args):
    global ids
    print(args)
    _mail = args[0]
    _id = args[1]
    
    with lock:
        ids[_mail] = _id



@socketio.on('text')
def connect(*args):
    text = args[0]
    sent_by = args[1]
    sent_for = args[2]
    
    print(ids)
    try:
        with lock:
            sent_for_id = ids[sent_for]

        socketio.emit('msg', {'content': text, 'sent_by':sent_by}, room=sent_for_id)
        
    except KeyError as e:
        # user is offline
        print(e)
        


    finally:    
        #write in db
        dm = DM(content=text, _from=sent_by, _to=sent_for, timestamp=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

    
        try:
            db.session.add(dm)
            db.session.commit()


        except Exception as e:
            db.session.rollback()
            print(e)



    

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



if __name__ == '__main__':
    socketio.run(app, port=9422, debug=True)
