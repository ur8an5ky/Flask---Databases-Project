from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_login import LoginManager

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Test123!@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine('postgresql://postgres:Test123!@localhost/postgres')
app.config['SECRET_KEY'] = '082493b92811db16ce037695'
db = SQLAlchemy(app)
login_manager = LoginManager(app)


from App import routes