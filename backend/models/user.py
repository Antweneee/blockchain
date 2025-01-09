from . import db, datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    xrpl_address = db.Column(db.String(35))
    xrpl_seed = db.Column(db.String(50))
    xrpl_balance = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'xrpl_address': self.xrpl_address,
            'xrpl_balance': self.xrpl_balance,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
