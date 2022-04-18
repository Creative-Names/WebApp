from flask import render_template, request, redirect, flash, Markup, Blueprint, url_for
from flask_login import login_required, current_user, logout_user
from models import User, db, Post, DM #type: ignore
from employerApp.employer_auth.employer_auth import employer_auth_bp #type: ignore
from config import Config #type: ignore
import datetime
import ast

HTTP_STATUS = Config.HTTP_STATUS
SERVER_NAME = Config.SERVER_NAME
employer_bp = Blueprint('employer_bp', __name__)


employer_bp.register_blueprint(employer_auth_bp)



def constructMD(title, desc, place, salary, no_people, contact):
#     return f"""\
# #### New job posting available as the **{title}**


# {desc}  
  
# #### **Estimated Salary:** {salary}  
# #### **Place of Work:** {place}  
# #### **Slots Filled:** 0/{no_people}  
# #### **Contact Information:** {contact}"""
    return f""" 
  

### New job posting available as **{title}**

---

{desc}
\

---

##### Here's the details:

- **Estimated Salary**: {salary}  
- **Place of Work**: {place}  
- **Candidates Required**: {no_people}  
- **Contact Information**: {contact}
"""


@employer_bp.route('/', subdomain='employer', strict_slashes=False, methods=['GET', 'POST'])
def home():
    if not current_user.is_authenticated:
        return render_template('employer_index.html')
    
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
        flash(Markup(
            f"<a href=\"{HTTP_STATUS}employer.{SERVER_NAME}?delete=True&confirm=True\" class=\"alert-link\">Delete Account Permanently? </a>"))
        return render_template('employer_index.html', dmmers=dmmers)
    

   
    if 'page' in request.args:

        req_page = request.args['page']

    else:
        req_page = 'posts'

    if req_page == 'posts':
        delid = None
        if request.method == "POST":
            try:
                delid = request.form['del']
                print(delid)
            except KeyError:
                delid = None

        if delid == None or request.method == "GET":

            posts = Post.query.filter_by(poster=current_user.email).all()

            for post in posts:

                email = post.poster
                post.poster_name = User.query.filter_by(
                    email=email, role='EMPLOYER').first().username
                # post.likers

                if post.likes == "":
                    post.likes="[]"

                likers_mails = ast.literal_eval(post.likes)
                post.likers = []
                
                for i in likers_mails:
                    post.likers.append(User.query.filter_by(
                    email=i).first())
                    
                
            return render_template('employer_recentPosts.html', posts=posts[::-1], dmmers=dmmers)

        try:
            print(delid)
            post = Post.query.filter_by(id=delid).delete()
            db.session.commit()

        except Exception as e:
            print(e)
            flash(Markup("There was some error in deleting the post"))
            posts = Post.query.filter_by(poster=current_user.email).all()
            for post in posts:
                email = post.poster
                post.poster_name = User.query.filter_by(
                    email=email, role='EMPLOYER').first().username
                
            if post.likes == "":
                post.likes="[]"

            likers_mails = ast.literal_eval(post.likes)
            post.likers = []
            
            for i in likers_mails:
                post.likers.append(User.query.filter_by(
                email=i, role='EMPLOYER').first())
                
            return render_template('employer_recentPosts.html', posts=posts[::-1], dmmers=dmmers)


        flash(Markup("Post deleted successfully"))
        posts = Post.query.filter_by(poster=current_user.email).all()
        for post in posts:
            email = post.poster
            post.poster_name = User.query.filter_by(
                email=email, role='EMPLOYER').first().username
            
            if post.likes == "":
                post.likes="[]"

            likers_mails = ast.literal_eval(post.likes)
            post.likers = []
            
            for i in likers_mails:
                post.likers.append(User.query.filter_by(
                email=i).first())
            
        return render_template('employer_recentPosts.html', posts=posts[::-1], dmmers=dmmers)


    elif req_page == 'new':
        if request.method == "POST":
            title = request.form['title']
            pcontent = request.form['pcontent']
            salary = request.form['salary']
            place = request.form['place']
            no_people = request.form['no_people']
            contact = request.form['contact']
            
            markdown = constructMD(title, pcontent, place, salary, no_people, contact)

            post = Post(poster=current_user.email, content=markdown,
                        timestamp=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), likes="", replies="")

            try:
                db.session.add(post)
                db.session.commit()
                flash(Markup("Post created successfully!"))

                return redirect(url_for('employer_bp.home', page='posts'))

            except Exception as e:
                db.session.rollback()
                print(e)
                flash(Markup(
                    f"There was some error in creating the post. Try again later"))
                return render_template('employer_create.html', dmmers=dmmers)

        return render_template('employer_create.html', dmmers=dmmers)

    elif req_page == 'followers':
        # posts = Post.query.filter(Post.content.contains('print')).all()
        pass
        # list followers

    elif req_page == 'chats':
        # list chats
        chatter = request.args['chat']
        user_chats = DM.query.filter(( (DM._from.contains(current_user.email) & DM._to.contains(chatter)) | ((DM._from.contains(chatter) & DM._to.contains(current_user.email))))).all()

        
        chattername = User.query.filter_by(email=chatter).first()
        if chattername is None:
            chattername = "Unknown User"
            
        return render_template('employerDM.html', dmmers=dmmers, chats=user_chats, chatter=chattername)
        
    elif req_page == 'newDM': 
        
        return render_template('employer_newDM.html', dmmers=dmmers)

    return render_template("employer_index.html", dmmers=dmmers)


@employer_bp.route('/update_details', subdomain='employer', methods=["GET", "POST"], strict_slashes=False)
@login_required   
def update_shopkeeper_details():

    if not current_user.is_authenticated:
        return render_template('employer_index.html')

    
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
                return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}')
            except:
                flash(Markup("There was some error! Try again later."))
                return render_template('employer_updateDetails.html', dmmers=dmmers)
        flash(Markup(
            f"<a href=\"{HTTP_STATUS}employer.{SERVER_NAME}/update_details?delete=True&confirm=True\" class=\"alert-link\">Delete Account Permanently? </a>"))
        return render_template('employer_updateDetails.html', dmmers=dmmers)

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
    return render_template('employer_updateDetails.html', username=username, about=about, dmmers=dmmers)


