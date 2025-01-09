from flask import Blueprint, jsonify, session
from models import User
from functools import wraps
from utils.auth import login_required

users_bp = Blueprint('users', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@users_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    user = User.query.get(session['user_id'])
    return jsonify({
        'username': user.username,
        'email': user.email,
        'xrpl_address': user.xrpl_address,
        'created_at': user.created_at
    })
