#Import all Necessary Modules
from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
import wtforms
from wtforms import validators

#Initialize the App and Database
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)
app.app_context().push()
with app.app_context():
    db.create_all()

#Information regarding hashing of passwords
app.config["SECRET_KEY"] = "thisisanotsosecretkey"
bcrypt = Bcrypt(app)

#Initialize Login Manager
login_mananager = LoginManager()
login_mananager.init_app(app)
login_mananager.login_view = "login"

@login_mananager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#User Class
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

#Class for the Registration Form
class Registration(FlaskForm):
    username = wtforms.StringField(validators=[validators.InputRequired(), validators.length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = wtforms.PasswordField(validators=[validators.InputRequired(), validators.length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = wtforms.SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()

        if existing_user_username:
            raise validators.ValidationError("That username already exists. Please choose a different one.")


#Class for the Login Form
class Login(FlaskForm):
    username = wtforms.StringField(validators=[validators.InputRequired(), validators.length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = wtforms.PasswordField(validators=[validators.InputRequired(), validators.length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = wtforms.SubmitField("Login")

#This is how we will route people to the webpage. To route to a new webpage, simply make a new version of this.
#We can also use these functions to make custom methods. Look up the flask documentation for how to pass variables in.
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html")

#App route to login page. Upon user submission of the form, if the user exists and can be validated, it redirects them to the dashboard page.
@app.route("/login", methods=["GET", "POST"])
def login():
    form = Login()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect("/dashboard")
    
    return render_template("login.html", form=form)

#App route to dashboard page. This is the default page all users are directed to upon login.
@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")

#App route to logout user. This route has no page content. If the user is logged in, it will automatically log them out and redirect them to the login page.
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = Registration()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html", form=form)

#This is is the program to run the server on a Localhost PC.
#We recommend that you run this on a virtual machine (NOTE: All VENV Folders are ignored) on Windows 10 or newer
if __name__ == "__main__":
    app.run()
