import os

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
)
from flask_login import login_user, logout_user, current_user

from app import db
from .forms import RegistrationForm, LoginForm
from .models import User


auth_blueprint = Blueprint(
    "auth", __name__, template_folder="../templates/auth", url_prefix="/auth"
)


@auth_blueprint.route("/register", methods=["POST", "GET"])
def register():
    """Registration page."""
    form = RegistrationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User(request.form["email"])
            user.set_password(request.form["password"])
            db.session.add(user)
            db.session.commit()
            # Generate user services folders
            user.create_folder()
            flash("You have been successfully registered, please log in.", "info")
            return redirect(url_for("auth.login"))
        else:
            flash("User with that name already exists.", "info")
    return render_template("registration.html", form=form)


@auth_blueprint.route("/login", methods=["POST", "GET"])
def login():
    """Login page."""
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=request.form["email"]).one()
            login_user(user)
            flash("You have been successfully logged in.", "info")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)


@auth_blueprint.route("/logout", methods=["POST", "GET"])
def log_out():
    """Logout user api."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
