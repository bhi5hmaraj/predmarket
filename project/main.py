from flask import Blueprint, render_template
from . import db
from flask_login import login_required, current_user
from .models import User


main = Blueprint('main', __name__)

...
@main.route('/')
def index():
    db.session.execute('SELECT * FROM User')
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)
