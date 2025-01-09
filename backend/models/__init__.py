from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Import all models here to expose them at the package level
from .user import User
from .asset import Asset
from .listing import Listing
from .transaction import Transaction
from .wallet import WalletTransaction

# Export all models
__all__ = ['db', 'User', 'Asset', 'Listing', 'Transaction', 'WalletTransaction']
