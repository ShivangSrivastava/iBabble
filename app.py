# Importing required modules
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField,IntegerField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import socket
import smtplib
import webbrowser
import random

# flask app
app = Flask(__name__)

# configure database
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# connecting to database
db = SQLAlchemy(app)

# for hashing password
bcrypt = Bcrypt(app)

# creating socket
socketio = SocketIO(app, cors_allowed_origins="*")

# configure secret key
app.config['SECRET_KEY'] = 'thisisasecretkey'

# login manager 
login_manager = LoginManager()

# initiate with app
login_manager.init_app(app) 
login_manager.login_view = 'login'


# load from database
@login_manager.user_loader
def load_user(username):
    return User.query.get(str(username))

# creating table for user and password 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email=db.Column(db.String(50), nullable=False, unique=True)
    name=db.Column(db.String(50), nullable=False)

# for signup of user
class SignupForm(FlaskForm):

    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    email = EmailField(validators=[
                             InputRequired(), Length(min=8, max=50)], render_kw={"placeholder": "Email"})
    name = StringField(validators=[
                             InputRequired(), Length(min=2, max=50)], render_kw={"placeholder": "Your Name"})
    
    submit = SubmitField('Signup')

    # checking user already exist or not 
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

# for login of user
class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


# socket commands
# recieving messages
@socketio.on('message')
def handle_message(msg):
    global allConnectedUsers
    if msg:
        if len(str(msg).split())==2:
            if str(msg).split()[1]=="3y738732y73628732679":
                user=str(msg).split()[0]
                msg=f"{user}!7gh7edyh7@$#^888y4Connected"
                send(msg, broadcast=True)
                return
        send(str(msg), broadcast=True)

# home page 
@app.route('/')
@login_required
def index():
    id_=current_user.get_id()
    username=User.query.filter_by(id=id_).first().username
    name=User.query.filter_by(id=id_).first().name
    return render_template('index.html',user=username,name=name)

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect('/')
            else:
                flash(u"Password is incorrect","error")
        else:
            flash(u"Username is incorrect or not signed up yet","error")
    return render_template('login.html', form=form)

# logout user
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# signup user
@ app.route('/signup', methods=['GET', 'POST'])
def signup():
    
    if current_user.is_authenticated:
        return redirect("/")
    form = SignupForm()
    if User.query.filter_by(username=form.username.data).first():
        flash(u"Username already used","error")
    if User.query.filter_by(email=form.email.data).first():
        flash(u"Email already used","error")
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data, 
            password=hashed_password, 
            email=form.email.data, 
            name=form.name.data,
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

class SendMail:
    def __init__(self):
        self.s = smtplib.SMTP('smtp.gmail.com', 587)
        
        # start TLS for security
        self.s.starttls()
        
        self._SENDER_EMAIL, _SENDER_PASSWORD = "email.ibabble@gmail.com","shivang@ibabble"
        # Authentication
        self.s.login(self._SENDER_EMAIL, _SENDER_PASSWORD)
        
    def sendMail(self,receiverEmail,message):
        # sending the mail
        self.s.sendmail(self._SENDER_EMAIL, receiverEmail, message)
        
        # terminating the session
        self.s.quit()
    def sendOTP(self,receiverEmail):
        otp=random.randint(100000, 999999)
        msg=f"Your varification code for registration in iBabble is {otp}"
        self.sendMail(receiverEmail,msg)
        return otp




def get_ip_address():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s.connect(("8.8.8.8", 80))

    return s.getsockname()[0]


if __name__ == "__main__":
    #Creating tables
    with app.app_context():
        db.create_all()
    IPAddress=get_ip_address()
    port=8000
    url=f"http://{IPAddress}:{port}"
    print("Running at", url)
    webbrowser.open_new_tab(url)
    socketio.run(app,debug=False, host=IPAddress,port=port)
