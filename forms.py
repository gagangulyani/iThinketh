from wtforms.validators import InputRequired, Email, Length, ValidationError
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField)
from flask_wtf.file import FileField, FileRequired, FileAllowed
from models.database import Database
from string import punctuation


def checkForJunk(form=None, field=None, usrtext=None):
    punct = punctuation
    if not field:
        field = {'data': usrtext}
    for i in field.data.replace('_', '').replace('-', ''):
        if i in punct:
            if usrtext:
                return True
            else:
                raise ValidationError(
                    'Only Alphabets, Numbers and Underscores Allowed!')


def StrongPassword(form, field):
    punct = punctuation
    numbers = "0123456789"
    alphabets = "QWERTYUIOPASDFGHJKLZXCVBNM"

    errors = {
        "isSpecial": 'Special Symbol',
        "isNumber": 'Number',
        'isUpper': 'UpperCase Character'
    }

    if any(char in field.data for char in punct):
        errors.pop('isSpecial')

    if any(char in field.data for char in numbers):
        errors.pop('isNumber')

    if any(char in field.data for char in alphabets):
        errors.pop('isUpper')

    if errors:
        message = "Password Must Contain atleast 1 "
        errors = [errors[msg] for msg in errors]
        extra = ", ".join(errors[:-1])
        if extra:
            extra2 = " and " + errors[-1]
        else:
            extra2 = errors[-1]

        message += extra + extra2

        raise ValidationError(message)


class SignupForm(FlaskForm):

    name = StringField(validators=[
        InputRequired('Please Enter your Name'),
        checkForJunk
    ], render_kw={"placeholder": "Enter Your Name"})

    username = StringField(validators=[
                           InputRequired('Please Enter a Username'),
                           checkForJunk
                           ], render_kw={"placeholder": "Choose a Username"})

    about = TextAreaField('Quote', render_kw={
                          "placeholder": "Tell us something about Yourself"})

    email = StringField(validators=[
        InputRequired('Please Enter your Email address'),
        Email('Please Enter a valid email address')
    ], render_kw={
        "placeholder": "Enter your Email"})

    password = PasswordField(validators=[
        InputRequired('Please Enter your Password'),
        Length(min=6, max=16,
               message='Password Must be 8-16\
 Characters Long'), StrongPassword],
        render_kw={"placeholder": "Enter Your Password"})

    submit = SubmitField("Signup",
                         validators=[
                             InputRequired()
                         ])


class LoginForm(FlaskForm):
    username = StringField(validators=[
        InputRequired(
            'Please Enter your Username Or Email'),
        Length(min=4, max=50,
               message='Invalid Username')],
        render_kw={"placeholder": "Enter Email Address or Username"})

    password = PasswordField("Password",
                             validators=[
                                 InputRequired('Please Enter your Password'),
                                 Length(min=6, max=16,
                                        message='Invalid Password')],
                             render_kw={"placeholder": "Enter Password"})

    submit = SubmitField("Login",
                         validators=[
                             InputRequired()
                         ])


Database.initialize('iThinketh')
# print(categories)


class UploadForm(FlaskForm):
    # category = SelectField("Category",
    #                        choices=categories,
    #                        validators=[
    #                            InputRequired('Please Choose a Category')])

    quote = TextAreaField('Quote',validators=[
                             InputRequired()
                         ],render_kw={"placeholder": "Enter your Quote here"})

    submit = SubmitField("Post",
                         validators=[
                             InputRequired()
                         ])
