from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


# app = Flask(__name__, static_folder='../../build', static_url_path='/')
app = Flask(__name__)
app.config['SECRET_KEY'] = "random_string"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booking_app.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
# This where redirect when login_required condition failed
login_manager.login_view = 'home'


from flask_backend.app_src import routes
