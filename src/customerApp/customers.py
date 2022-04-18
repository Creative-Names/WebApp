from flask import render_template, request, redirect, flash, Markup, Blueprint, url_for
from flask_login import login_required, current_user, logout_user
from models import db, User, DM, Post #type: ignore
from customerApp.customer_auth.customer_auth import customer_auth_bp #type: ignore
from config import Config #type: ignore
import datetime
import ast

HTTP_STATUS = Config.HTTP_STATUS
SERVER_NAME = Config.SERVER_NAME


customer_bp = Blueprint('customer_bp', __name__)


customer_bp.register_blueprint(customer_auth_bp)

@customer_bp.route('/', subdomain='explore', strict_slashes=False, methods=['GET', 'POST'])
def home():
    if not current_user.is_authenticated:
        return render_template('explorer_index.html')
    
    # get dms
    dms = DM.query.filter((DM._from.contains(current_user.email) | (DM._to.contains(current_user.email)))).all()
    dmmers = []

    for dm in dms:  
        if dm._to == current_user.email:
            dmmers.append(dm._from)
        elif dm._from == current_user.email:
            dmmers.append(dm._to)
    
    dmmers = list(dict.fromkeys(dmmers))[::-1]
    
    for i, dm in enumerate(dmmers):
        uname = User.query.filter_by(email=dm).first()
        if not uname:
            deluser = User()
            deluser.username = 'Unknown User'
            deluser.email = dm
            dmmers[i] = deluser
            
        else:
            dmmers[i] = uname
    

    if request.args.get('delete') == 'True':
        if request.args.get('confirm') == 'True':
            try:
                db.session.delete(current_user)
                db.session.commit()
                logout_user()
                return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}')
            except:
                flash(Markup("There was some error! Try again later."))
                return render_template('employer_index.html', dmmers=dmmers)
        flash(Markup(f"<a href=\"{HTTP_STATUS}explore.{SERVER_NAME}?delete=True&confirm=True\" class=\"alert-link\">Delete Account Permanently? </a>"))
        return render_template('explorer_index.html', dmmers=dmmers)

    if 'page' in request.args:
        
        req_page = request.args['page']
        
    else:
        req_page = 'home'
        
        
    if req_page == 'home':
        likeID = None
        if request.method == "POST":
            try:
                likeID = request.form['interested']
            except KeyError:
                likeID = None

        if likeID == None or request.method == "GET":

            posts = Post.query.all()
            for post in posts:
                email = post.poster
                try:
                    post.poster_name = User.query.filter_by(
                        email=email, role='EMPLOYER').first().username
                except:
                    post.poster_name = "Unknown User"

                likestr = post.likes

                if likestr == "":
                    post.isLiked=False
            
                elif current_user.email in ast.literal_eval(likestr):
                
                    post.isLiked=True

                else:
                    post.isLiked=False

                return render_template('explorer_home.html', posts=posts[::-1], dmmers=dmmers)

        try:
            post = Post.query.filter_by(id=likeID).first()
            print(post)
            if post is None:
                posts = Post.query.all()
                for i in posts:
                    email = post.poster


                    try:
                        i.poster_name = User.query.filter_by(
                            email=email, role='EMPLOYER').first().username
                    except:
                        i.poster_name = "Unknown User"

                    likestr = post.likes


                    if likestr == "":
                        i.isLiked=False
                
                    elif current_user.email in ast.literal_eval(likestr):
                    
                        i.isLiked=True

                    else:
                        i.isLiked=False

                    return render_template('explorer_home.html', posts=posts[::-1], dmmers=dmmers)
                return render_template('explorer_home.html', posts=posts[::-1], dmmers=dmmers)


            print('h')
            old_likes = post.likes
            print('e')

            if old_likes == "":
                old_likes = "[]"
            likes_list = ast.literal_eval(old_likes)
            
            if current_user.email in likes_list:
                likes_list.remove(current_user.email)
            else:
                likes_list.append(current_user.email)

            new_likes = str(likes_list)

            post.likes = new_likes

            db.session.commit()
            flash(Markup("The company has been notified about your interest!"))


        except Exception as e:
            print(e)
            flash(Markup("There was some error in completing the operation"))
            posts = Post.query.all()
            print(posts)
            for post in posts: 
                email = post.poster 


                try:
                    post.poster_name = User.query.filter_by(
                        email=email, role='EMPLOYER').first().username
                except:
                    post.poster_name = "Unknown User"

                likestr = post.likes


                if likestr == "":
                    post.isLiked=False
            
                elif current_user.email in ast.literal_eval(likestr):
                
                    post.isLiked=True

                else:
                    post.isLiked=False

                return render_template('explorer_home.html', posts=posts[::-1], dmmers=dmmers)

        posts = Post.query.all()
        for post in posts:
            email = post.poster

            try:
                post.poster_name = User.query.filter_by(
                    email=email, role='EMPLOYER').first().username
            except:
                post.poster_name = "Unknown User"

            likestr = post.likes

            if likestr == "":
                post.isLiked=False
            
            elif current_user.email in ast.literal_eval(likestr):
                
                post.isLiked=True

            else:
                post.isLiked=False

            return render_template('explorer_home.html', posts=posts[::-1], dmmers=dmmers)


    
    elif req_page == 'following':
        # posts = Post.query.filter(Post.content.contains('print')).all()
        pass
    
        
    elif req_page == 'chats':
        # list chats
        chatter = request.args['chat']
        user_chats = DM.query.filter(( (DM._from.contains(current_user.email) & DM._to.contains(chatter)) | ((DM._from.contains(chatter) & DM._to.contains(current_user.email))))).all()

        
        chattername = User.query.filter_by(email=chatter).first()
        if chattername is None:
            chattername = "Unknown User"
            
        return render_template('explorerDM.html', dmmers=dmmers, chats=user_chats, chatter=chattername)
        
    elif req_page == 'newDM':
        
        return render_template('explorer_newDM.html', dmmers=dmmers)

    return render_template("explorer_index.html", dmmers=dmmers)

    






@customer_bp.route('/update_details', subdomain='explore', methods=["GET", "POST"], strict_slashes=False)
@login_required
def update_shopkeeper_details():

    if not current_user.is_authenticated:
        return render_template('explorer_updateDetails.html')

    # get dms
    dms = DM.query.filter((DM._from.contains(current_user.email) | (DM._to.contains(current_user.email)))).all()
    dmmers = []
    for dm in dms:
        if dm._to == current_user.email:
            dmmers.append(dm._from)
        elif dm._from == current_user.email:
            dmmers.append(dm._to)
    
    dmmers = list(dict.fromkeys(dmmers))[::-1]
    
    for i, dm in enumerate(dmmers):
        uname = User.query.filter_by(email=dm).first()
        if not uname:
            dmmers[i] = 'Unknown User'
        else:
            dmmers[i] = uname

    if request.args.get('delete') == 'True':
        if request.args.get('confirm') == 'True':
            try:
                db.session.delete(current_user)
                db.session.commit()
                logout_user()
                return redirect(f'{HTTP_STATUS}v.{SERVER_NAME}')
            except:
                flash(Markup("There was some error! Try again later."))
                return render_template('explorer_updateDetails.html')
        flash(Markup(f"<a href=\"{HTTP_STATUS}explore.{SERVER_NAME}/update_details?delete=True&confirm=True\" class=\"alert-link\">Delete Account Permanently? </a>"))
        return render_template('explorer_updateDetails.html')


    if request.method == "POST":
        current_user.username = request.form['uname']
        current_user.about = request.form['loc']

        try:
            db.session.commit()
            flash(Markup("Your details have been updated successfully!"))
        except:
            flash(
                Markup("There was some error in updating your details. Try again later!"))

    username = current_user.username
    about = current_user.about
    return render_template('explorer_updateDetails.html', username=username, about=about, dmmers=dmmers)

