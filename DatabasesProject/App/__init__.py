from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_login import LoginManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://u0urbanski:0urbanski@localhost/u0urbanski'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine('postgresql://u0urbanski:0urbanski@localhost/u0urbanski')
app.config['SECRET_KEY'] = '082493b92811db16ce037695'
db = SQLAlchemy(app)
login_manager = LoginManager(app)


from App import routes