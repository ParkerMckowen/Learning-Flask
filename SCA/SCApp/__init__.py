from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' #gives the location of the login page for when someone accesses a login required page

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = '587'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'parkersmicroblog@gmail.com'
app.config['MAIL_PASSWORD'] = 'ParkersMicroblog123'
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') # can also set these two as environment variables then get them using the os module
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)


from SCApp import routes #To avoid circular imports, the app is imported to the routes before the routes are imported, think chicken before egg thing