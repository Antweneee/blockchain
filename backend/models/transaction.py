from . import db, datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    price = db.Column(db.Numeric(20, 6), nullable=False)
    xrpl_transaction_hash = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    listing = db.relationship('Listing', backref='transactions')
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='purchases')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='sales')

    def complete(self, session):
        try:
            self.status = 'completed'
            listing = self.listing
            asset = listing.asset

            listing.status = 'completed'
            asset.owner_id = self.buyer_id
            asset.status = 'active'

            session.add_all([self, listing, asset])
            session.commit()

            session.refresh(asset)
            if asset.owner_id != self.buyer_id:
                raise Exception("Asset ownership verification failed")

            return True

        except Exception as e:
            session.rollback()
            self.status = 'failed'
            session.add(self)
            session.commit()
            raise e
