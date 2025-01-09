from . import db, datetime

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(20, 6), nullable=False)
    status = db.Column(db.String(20), default='completed')
    xrpl_transaction_hash = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='wallet_transactions')
