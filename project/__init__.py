from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres+psycopg2://postgres:^F!zYogjW8aNvNJE2HePXRkr@^woAnaRMqJo7Gdez9#mwCiTWLDkrcff3Vn@localhost:5432/predmarket_dev'
    app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '1033729897103355',
        'secret': '54ba48189e7773353b739f8836fffe5d'
    },
}

    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the pip install requests-oauthlibimary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
