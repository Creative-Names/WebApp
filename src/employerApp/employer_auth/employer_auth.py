from models import User
from flask import request, Blueprint, redirect, flash, Markup, render_template, url_for
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db
from sqlalchemy import exc
from email_.email import Email
from config import Config 
from utils import encrypt_file, decrypt_file
 
HTTP_STATUS = Config.HTTP_STATUS
SERVER_NAME = Config.SERVER_NAME

employer_auth_bp = Blueprint('employer_auth_bp', __name__) 

mail = Email()

# employer.hackathon5.com

@employer_auth_bp.route('/register', subdomain='employer', methods=["GET", "POST"], strict_slashes=False)
def register():

    if current_user.is_authenticated:
        return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}')

    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        about = request.form['about']
        pwd1 = request.form['password_set']
        pwd2 = request.form['password_confirm']

        emailIsUnique = User.query.filter_by(email=email, role='EMPLOYER').first()
        emailIsCustomer = User.query.filter_by(email=email, role='EMPLOYEE').first()

        if not emailIsUnique is None:
            flash(Markup(
                "An account already exists with this email. <a href=\"/login\" class=\"alert-link\">Login Here.</a>"))
            return render_template('employer_register.html')


        if not emailIsCustomer is None:
            flash(Markup(
                f"This email is already registered as a Customer. <a href=\"{HTTP_STATUS}explore.{SERVER_NAME}/login\" class=\"alert-link\">Login Here.</a> Or try to register with a different email-id."))
            return render_template('explorer_register.html')

        elif email == "":
            flash("Please enter a valid email-id.")
            return render_template('employer_register.html')


        elif pwd1 != pwd2:
            flash("The passwords do not match. Try Again.")
            return render_template('employer_register.html')

        elif len(pwd1) < 8:
            flash(
                "For the password to be safe, it needs to be atleast 8 characters long!")
            return render_template('employer_register.html')

        if not any(i.isdigit() for i in pwd1):
            flash("For the password to be safe, it needs contain numeric characters!")
            return render_template('employer_register.html')

        try:
            otp = mail.send_registration_otp(email)
            try:
                decrypt_file('otps.txt')
            except Exception as e:
                print(e)
            with open('otps.txt', 'a') as f:
                f.write(email + '___!!!___' + pwd1+ '___!!!___' + otp + '\n')
            encrypt_file('otps.txt')
            

            return redirect(url_for('employer_bp.employer_auth_bp.verify_reg_otp', email=email, username=name, about=about))

        except Exception as e:
            print(e)
            flash(Markup("There was a connection error. Please try agin later"))
            return render_template('employer_register.html')

    return render_template('employer_register.html')


@employer_auth_bp.route('/register/verify_otp', subdomain='employer', methods=["GET", "POST"], strict_slashes=False)
def verify_reg_otp():

    if current_user.is_authenticated:
        return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}')

    if request.method == 'POST':
        
        user_otp = request.form['otp']
        
        try:
            mail = request.args['email']
            name = request.args['username']
            about = request.args['about']
        except KeyError:
            flash(Markup("email not found, please don\'t tamper with the url"))

            return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}/register')

        try:
            decrypt_file('otps.txt')
        except Exception as e:
            print(e)
            
        f = open('otps.txt', 'r')
        lines = f.readlines()
        f.close()
        
        encrypt_file('otps.txt')
        
        otps = {}
            
        def makeDict(x):
            splitted = x.split('___!!!___')
            otps[splitted[0]] = (splitted[1], splitted[2].strip())
            
        list(map(makeDict, lines))
        
        if mail not in list(otps.keys()):
            flash(Markup("otp not found, try to get otp again by registering again"))
            return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}/register')


        if otps[mail][1] != user_otp:
            flash(Markup(
                f"Wrong OTP. Try Again. Or <a href=\"{HTTP_STATUS}employer.{SERVER_NAME}/register\" class=\"alert-link\">Click here</a> to start over.</a>"))
            return render_template('employer_verifyOtp.html')
        
        if otps[mail][1] == user_otp:

            employer = User(email=mail, password=generate_password_hash(otps[mail][0].strip()), username=name, 
                                role="EMPLOYER", about=about, relations = "", date_joined=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

            try:
                db.session.add(employer)
                db.session.commit()
                flash(Markup(
                    f"Account created successfully! <a href=\"{HTTP_STATUS}employer.{SERVER_NAME}/login\" class=\"alert-link\">Login Here.</a>"))

                decrypt_file('otps.txt')

                with open('otps.txt', 'w+') as f:
                    pendings = f.readlines()
                    for i in pendings:
                        if mail in i:
                            pendings.remove(i)
                
                
                    f.seek(0)  

                    f.writelines(pendings)
            
                encrypt_file('otps.txt')


                return render_template('employer_verifyOtp.html')

            except exc.IntegrityError:
                db.session.rollback()
                flash(Markup(
                    f"An account already exists with this email. <a href=\"{HTTP_STATUS}employer.{SERVER_NAME}/login\" class=\"alert-link\">Login Here.</a>"))
                return render_template('employer_verifyOtp.html')

    return render_template('employer_verifyOtp.html')



@employer_auth_bp.route('/login', subdomain='employer', methods=["GET", "POST"], strict_slashes=False)
def login():
    if current_user.is_authenticated:
        return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}')
    if request.method == "POST":
        login_email = request.form['email']
        login_password = request.form['password']
        user = User.query.filter_by(email=login_email, role='EMPLOYER').first()
        if user is None:
            flash(Markup(
                f"This Email is not registered yet! <a href=\"{HTTP_STATUS}employer.{SERVER_NAME}/register\" class=\"alert-link\">Signup Here</a>"))
            return render_template('employer_login.html')

        pwd_check = check_password_hash(user.password, login_password)

        if pwd_check:
            try:
                logout_user()
            except Exception as e:
                print(e)
            try:
                login_user(user)

                flash(Markup(f"Welcome Back, {current_user.username}!"))
                return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}?page=posts')
            except Exception as e:
                print(e)
                flash(
                    Markup("We're having some trouble signing you in. Try again later."))
                return render_template('employer_login.html')

        flash(Markup("Wrong Password! Try agin"))
        return render_template('employer_login.html')

    return render_template('employer_login.html')


@employer_auth_bp.route('/forgotPwd', subdomain='employer', methods=["GET", "POST"], strict_slashes=False)
def recover_password():
    
    
    if current_user.is_authenticated:
        return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}')

    if request.method == 'POST':
        rec_email = request.form['rec_email']
        try:
            otp = mail.send_recovery_password(rec_email)
            try:
                decrypt_file('forgotPwdOtps.txt')
            except Exception as e:
                print(e)
            with open('forgotPwdOtps.txt', 'a') as f:
                f.write(rec_email + '___!!!___' + otp + '\n')
            encrypt_file('forgotPwdOtps.txt')

            return redirect(url_for("employer_bp.employer_auth_bp.verify_shopkeeper_rec_otp", email = rec_email))

        except Exception as e:
            print(e)
            flash(Markup("There was a connection error. Please try agin later"))
            return render_template('employer_forgotPwd.html')

    return render_template("employer_forgotPwd.html")


@employer_auth_bp.route('/forgotPwd/verify_otp', subdomain='employer', methods=["GET", "POST"], strict_slashes=False)
def verify_shopkeeper_rec_otp():
    

    if current_user.is_authenticated:
        return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}')

    
    if request.method == 'POST':
        user_rec_otp = request.form['otp']
        rec_mail = request.args['email']
        

        try:
            decrypt_file('forgotPwdOtps.txt')
        except Exception as e:
            print(e)
            
        f = open('forgotPwdOtps.txt', 'r')
        lines = f.readlines()
        f.close()
        
        encrypt_file('forgotPwdOtps.txt')
        
        otps = {}
            
        def makeDict(x):
            splitted = x.split('___!!!___')
            otps[splitted[0]] = splitted[1].strip()
            
        list(map(makeDict, lines))
        
        
        
        if rec_mail not in list(otps.keys()):
            flash(Markup("otp not found, try to get otp again."))
            return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}/forgotPwd')

        if otps[rec_mail] != user_rec_otp:
            flash(Markup(
                f"Wrong OTP. Try Again. Or <a href=\"{HTTP_STATUS}employer.{SERVER_NAME}/forgotPwd\" class=\"alert-link\">Click here</a> to start over.</a>"))
            return render_template('employer_verifyOtp.html')
        
        if otps[rec_mail] == user_rec_otp:
       
        
            user = User.query.filter_by(email=rec_mail, role='EMPLOYER').first()
            
            login_user(user)
            return redirect(f'{HTTP_STATUS}employer.{SERVER_NAME}')

    return render_template("employer_verifyRecoveryOtp.html")


@employer_auth_bp.route('/logout', subdomain='employer', strict_slashes=False)
@login_required
def logout():
    logout_user()
    return redirect(f"{HTTP_STATUS}employer.{SERVER_NAME}")


