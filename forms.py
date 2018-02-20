from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, TextField,
                    DateTimeField, IntegerField, TextAreaField)
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class NewEntryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    time_spent = IntegerField('Time Spent', validators=[DataRequired()])
    what_i_learned = TextAreaField('What I Learned', validators=[DataRequired()])
    resources_to_remember = TextAreaField('Resources To Remember', validators=[DataRequired()])
    tags = StringField('Tags')


class EditEntryForm(FlaskForm):
    title = StringField('Title')
    date = StringField('Date')
    time_spent = StringField('Time Spent')
    what_i_learned = TextAreaField('What I Learned')
    resources_to_remember = TextAreaField('Resources To Remember')
    tags = StringField('Tags')
