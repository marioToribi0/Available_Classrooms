from flask import Flask, redirect, render_template, request, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, ClassForm, ForgetPassword, ForgetUser
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from datetime import datetime
from functools import wraps

#ENVIROMENT VARIABLES
from os import environ
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

secret_key = environ["SECRET_KEY"]

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

##CELERY TO TASK asynchronously
from tasks import send_email_message, EMAIL,GMAIL,PASSWORD

##CONNECT TO DB
try:
    URI = environ["DATABASE_URL"]
    if (URI.startswith("postgres")):
        URI = f"postgresql{URI.split('postgres')[1]}"
    app.config["SQLALCHEMY_DATABASE_URI"] = URI
except KeyError:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DATABASE
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    premium = db.Column(db.Boolean(), default=True)
    date = db.Column(db.String(100), default=datetime.now().strftime("%d %B %Y"))

db.create_all()    

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
## This is used to store the information in current_user
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

# ONLY ADMIN
def only_admin(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        user = current_user
        id = None
        if (not user.is_anonymous):
            id = user.id
        if id==None or id!=1:
            abort(401)
        return function(*args, **kwargs)
    
    return wrapper

@app.route("/")
def index():
    return render_template("index.html", user=current_user)

@app.route("/about", methods=["POST", "GET"])
def about():
    if request.method == "POST":
        body = f"\nHi, Mario. \nMail: {request.form['email']}\n"
        send_email_message("Someone want to meet you...", body, GMAIL)
    return render_template("about.html", user=current_user)

@app.route("/feature", methods=["POST", "GET"])
def feature():
    form = ClassForm()
    results = False
    data = None
    if (request.method == "POST"):
        # Add and send data to html
        day = form.day.data
        hour = form.from_hour.data
        area = form.area.data
        comprobate = True if request.form.get("comprobate")!=None else None
        until = form.until_hour.data
        comprobate_before= True if request.form.get("comprobate_before")!=None else None     
        data = {"day": day, "hour": hour, "area": area, "comprobate": comprobate, "until": until, "comprobate_before": comprobate_before}
        results = True   
        
        # Comprobate status
        if (int(hour.split(":")[0])>int(until.split(":")[0])):
            flash('"From" cannot be greater than "Until"', category="error")
            results = False
        
    return render_template("feature.html",form=form, user=current_user, data=data, results=results)

@app.route("/contact")
def contact():
    return render_template("contact.html", user=current_user)

@app.route("/log_in", methods=["POST", "GET"])
def log_in():
    form = LoginForm()
    if (request.method=="POST"):
        email = form.email.data.lower()
        password = form.password.data

        # Search email
        user = User.query.filter_by(email=email).first()

        # Email exists
        if (user!=None):
            if (check_password_hash(user.password, password)):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Password doesn't match the user", category="error")
        else:
            flash("That user doesn't exist in our records", category="error")
            
    return render_template("log_in.html", form=form, user=current_user)

@app.route("/sign_up", methods=["POST", "GET"])
def sign_up():
    form = RegisterForm()
    if (form.validate_on_submit()):
        email = form.email.data.lower()
        password = form.password.data
        name = form.name.data

        password = generate_password_hash(password, salt_length=5)

        # Unique email
        if (User.query.filter_by(email=email).first() == None):
            new_user = User(
                name = name,
                email = email,
                password = password
            )
            # Add new user
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)
            
            return redirect(url_for("index"))
        else:
            flash("You already have an account with that email", category="error")
            return redirect(url_for("log_in"))
    return render_template("sign_up.html", form=form, user=current_user)

@app.route("/sign_off")
def sign_off():
    logout_user()
    return redirect(url_for('index'))

@app.route("/users", methods=["POST", "GET"])
@only_admin
def users():
    if (request.method=="POST"):
        id = request.form.get("user_id")
        # Verificate if it's a correct POST method
        if (id != None):
            user = User.query.filter_by(id=int(id)).first()
            
            # Invert status
            user.premium = not user.premium
            
            db.session.commit()

    users = User.query.all()
    return render_template("users.html", user=current_user, users= users)

@app.route("/forget_password", methods=["GET", "POST"])
def forget_password():
    form = ForgetPassword()
    if request.method=="POST":
        new_password = form.new_password.data
        id = request.args.get("id", None)
        user = User.query.filter_by(id=id).first()
        
        if (user!=None):
            user.password = generate_password_hash(new_password, salt_length=5)
            db.session.commit()
            
            login_user(user)
            redirect(url_for('index'))
        else:
            flash("Has occured an error", "error")
        
    else:
        password = request.args.get("code", None)
        user_id = request.args.get("user", None)
        user = User.query.filter_by(id=user_id).first()
        comprobation = password==user.password if user!=None else False
        
        # Abort if there aren't access
        if user_id == None or password == None or not comprobation:
            abort(401)
    return render_template("forget_password.html", user=current_user, form=form, user_to_change=user)

@app.route("/forget_user", methods=["POST", "GET"])
def forget_user():
    form = ForgetUser()
    if request.method=="POST":
        user = form.user.data.lower()
        user = User.query.filter_by(email=user).first()
        
        # Not found user
        if (user==None):
            flash("Not found this user in our records", "error")
        else:
            # Generate the url and send
            url = f"{request.url_root[:-1]}{url_for('forget_password', code = user.password, user = user.id)}"
            body = f"\nHello {user.name}, enter the following link to restore your password.\nURL: {url}\n"
            send_email_message("Change password", body, user.email)
            flash("Wait a minutes, we send you an email", "success")
            
    return render_template("forget_user.html", user=current_user, form=form)

if (__name__=="__main__"):
    app.run(port=5000)
