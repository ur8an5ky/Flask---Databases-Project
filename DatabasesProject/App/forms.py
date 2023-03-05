from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import Length, DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[Length(min=4, max=5), DataRequired()])
    password = PasswordField(label='Haslo', validators=[Length(min=10, max=11), DataRequired()])
    submit = SubmitField(label='Zaloguj sie')
