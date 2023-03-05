from App import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id):
    return Admin.query.get(int(id))

class Admin(db.Model, UserMixin):
    __table_args__ = {"schema":"mundial"}
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=5), nullable=False, unique=True)
    password = db.Column(db.String(length=11), nullable=False, unique=True)