from . import db, datetime

class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    token_id = db.Column(db.String(64), unique=True, index=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship('User', foreign_keys=[owner_id], backref=db.backref('assets', lazy=True))
    listings = db.relationship('Listing', backref='asset', lazy=True, cascade="all, delete-orphan")

    def transfer_ownership(self, new_owner_id, session):
        try:
            old_owner_id = self.owner_id
            self.owner_id = new_owner_id
            self.updated_at = datetime.utcnow()
            self.status = 'active'

            for listing in self.listings:
                if listing.status == 'active':
                    listing.status = 'completed'

            session.add(self)
            session.commit()

            session.refresh(self)
            if self.owner_id != new_owner_id:
                raise Exception(f"Ownership transfer verification failed. Expected: {new_owner_id}, Got: {self.owner_id}")

            return True

        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to transfer asset ownership: {str(e)}")

    def get_active_listing(self):
        """Get the current active listing for this asset, if any"""
        return next((listing for listing in self.listings if listing.status == 'active'), None)

    def is_owned_by(self, user_id):
        """Check if the asset is owned by the given user"""
        return self.owner_id == user_id

    def can_be_listed(self):
        """Check if the asset can be listed for sale"""
        if self.status not in ['active']:
            return False, "Asset is not in an active state"

        active_listing = self.get_active_listing()
        if active_listing:
            return False, "Asset is already listed for sale"

        if not self.token_id:
            return False, "Asset does not have a valid token ID"
        return True, None
