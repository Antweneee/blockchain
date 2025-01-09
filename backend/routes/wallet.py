from flask import Blueprint, request, jsonify, session
from models import db, WalletTransaction, User
from decimal import Decimal
from utils.auth import login_required
from utils.xrpl_utils import get_account_balance

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    try:
        transactions = WalletTransaction.query.filter_by(user_id=session['user_id']).order_by(WalletTransaction.created_at.desc()).all()

        return jsonify([{
            'id': tx.id,
            'type': tx.transaction_type,
            'amount': str(tx.amount),
            'status': tx.status,
            'xrpl_transaction_hash': tx.xrpl_transaction_hash,
            'created_at': tx.created_at.isoformat()
        } for tx in transactions])

    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        return jsonify({'error': 'Failed to fetch transactions'}), 500

@wallet_bp.route('/deposit', methods=['POST'])
@login_required
def create_deposit():
    """Record a deposit transaction for the logged-in user."""
    data = request.get_json()

    transaction = WalletTransaction(
        user_id=session['user_id'],
        transaction_type='deposit',
        amount=Decimal(data['amount']),
        xrpl_transaction_hash=data['xrpl_transaction_hash']
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        'message': 'Deposit recorded successfully',
        'transaction_id': transaction.id
    }), 201

@wallet_bp.route('/balance', methods=['GET'])
@login_required
def get_balance():
    """Fetch the XRP balance of the logged-in user's XRPL account."""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        balance = get_account_balance(user.xrpl_address)

        if balance != user.xrpl_balance:
            user.xrpl_balance = balance
            db.session.commit()

        return jsonify({'balance': str(balance)})

    except Exception as e:
        return jsonify({'error': 'Failed to fetch balance', 'details': str(e)}), 500
