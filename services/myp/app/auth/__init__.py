from flask_login import LoginManager, AnonymousUserMixin
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()


login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.session_protection = "strong"
login_manager.login_message = "Please login to access to this page"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    """Check if user exist on DB."""
    from .models import User

    return User.query.get(user_id)


class Anonymous(AnonymousUserMixin):
    """Helps to deal with non register user."""

    def __init__(self):
        self.username = "Guest"


def create_module(app, **kwargs):
    from .controllers import auth_blueprint

    bcrypt.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_blueprint)
