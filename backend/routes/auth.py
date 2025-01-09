from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from utils.xrpl_utils import create_xrpl_account, get_account_balance
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        logger.debug(f"Registration attempt for email: {data.get('email')}")

        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400

        xrpl_account = create_xrpl_account()
        if not xrpl_account:
            logger.error("Failed to create XRPL account")
            return jsonify({'error': 'Failed to create XRPL wallet'}), 500

        logger.debug(f"XRPL account created: {xrpl_account['address']} with balance: {xrpl_account['balance']} XRP")

        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            xrpl_address=xrpl_account['address'],
            xrpl_seed=xrpl_account['seed'],
            xrpl_balance=xrpl_account['balance']
        )

        db.session.add(user)
        db.session.flush()

        session['user_id'] = user.id
        session.permanent = True

        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'xrpl_address': user.xrpl_address,
                'xrpl_balance': str(user.xrpl_balance)
            }
        }), 201

    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        logger.debug(f"Login attempt for email: {data.get('email')}")

        user = db.session.query(User).filter(User.email == data['email']).first()

        logger.debug(f"User found: {user is not None}")

        if user and check_password_hash(user.password_hash, data['password']):
            logger.debug("Password verified successfully")

            session.clear()
            logger.debug("Session cleared")

            session['user_id'] = user.id
            session.permanent = True
            logger.debug(f"New session set with user_id: {user.id}")

            try:
                balance = get_account_balance(user.xrpl_address)
                logger.debug(f"Retrieved balance: {balance}")
                if balance != user.xrpl_balance:
                    user.xrpl_balance = balance
                    db.session.commit()
            except Exception as balance_error:
                logger.warning(f"Error updating balance: {str(balance_error)}")
                balance = user.xrpl_balance

            response_data = {
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'xrpl_address': user.xrpl_address,
                    'xrpl_balance': str(balance)
                }
            }
            logger.debug(f"Sending response: {response_data}")
            return jsonify(response_data)

        logger.debug("Invalid credentials")
        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/check-balance', methods=['GET'])
def check_balance():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        balance = get_account_balance(user.xrpl_address)
        if balance != user.xrpl_balance:
            user.xrpl_balance = balance
            db.session.commit()

        return jsonify({
            'address': user.xrpl_address,
            'balance': str(balance)
        })

    except Exception as e:
        logger.error(f"Balance check error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to check balance'}), 500
