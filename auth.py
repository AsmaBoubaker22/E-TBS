from functools import wraps
from flask import redirect, session, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  
            flash('Please login first to access this page!', category='E')
            return redirect('/')  # Directly redirect to home.html
        return f(*args, **kwargs)
    return decorated_function