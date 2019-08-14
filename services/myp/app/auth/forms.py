"""Authentication forms."""

from flask import flash
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_wtf import FlaskForm as Form

from .models import User

#########################
# Authentication
#########################


class RegistrationForm(Form):
    """User register."""

    email = StringField("Your email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=1)])
    confirm = PasswordField(
        "Confirm your password", validators=[DataRequired(), EqualTo("password")]
    )

    def validate(self):
        """Validate if user already exist on DB."""
        check_validate = super(RegistrationForm, self).validate()

        if not check_validate:
            return False

        user = User.query.filter_by(email=self.email.data).first()

        if user:
            return False
        return True


class LoginForm(Form):
    """User register."""

    email = StringField("Your email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=1)])

    def validate(self):
        """Check if password if correct."""
        check_validate = super(LoginForm, self).validate()

        # If all validators didn't return all True
        if not check_validate:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        # Check if the user exist
        if not user:
            return False
        if not user.check_password(self.password.data):
            return False
        return True
