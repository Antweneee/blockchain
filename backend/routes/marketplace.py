from flask import Blueprint, request, jsonify, session
from models import db, Listing, Asset, Transaction, User, WalletTransaction
from utils.auth import login_required
from utils.xrpl_utils import create_sell_offer, accept_buy_offer
from xrpl.wallet import Wallet
from decimal import Decimal
import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

marketplace_bp = Blueprint('marketplace', __name__)

@marketplace_bp.route('/listings', methods=['POST'])
@login_required
def create_listing():
    try:
        logger.info("Starting listing creation")
        data = request.get_json()
        logger.debug(f"Received data: {data}")

        user = User.query.get(session['user_id'])
        asset = Asset.query.get(data['asset_id'])

        if not asset:
            return jsonify({'error': 'Asset not found'}), 404

        if not asset.is_owned_by(user.id):
            return jsonify({'error': 'You do not own this asset'}), 403

        can_list, reason = asset.can_be_listed()
        if not can_list:
            return jsonify({'error': reason}), 400

        logger.info(f"Creating XRPL offer for token {asset.token_id}")
        wallet = Wallet.from_seed(user.xrpl_seed)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            offer_result = loop.run_until_complete(
                create_sell_offer(
                    wallet=wallet,
                    token_id=asset.token_id,
                    price=float(data['price'])
                )
            )
            logger.info(f"XRPL offer created: {offer_result}")
            logger.debug(f"Offer ID to be stored: {offer_result['offer_id']}")
        finally:
            loop.close()

        logger.info("Creating database listing")
        listing = Listing(
            asset_id=asset.id,
            seller_id=user.id,
            price=Decimal(data['price']),
            status='active',
            offer_id=offer_result['offer_id']
        )

        asset.status = 'listed'

        db.session.add(listing)
        db.session.commit()

        logger.info(f"Listing created successfully with ID: {listing.id}")
        return jsonify({
            'message': 'Listing created successfully',
            'listing': {
                'id': listing.id,
                'price': str(listing.price),
                'offer_id': listing.offer_id
            }
        }), 201
    except Exception as e:
        logger.error(f"Error creating listing: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/listings', methods=['GET'])
def get_listings():
    try:
        listings = Listing.query.filter_by(status='active').all()
        response = [{
            'id': listing.id,
            'asset': {
                'id': listing.asset.id,
                'title': listing.asset.title,
                'description': listing.asset.description,
                'image_url': listing.asset.image_url,
                'token_id': listing.asset.token_id
            },
            'price': str(listing.price),
            'seller': {
                'id': listing.seller.id,
                'username': listing.seller.username
            },
            'status': listing.status,
            'offer_id': listing.offer_id,
            'created_at': listing.created_at.isoformat()
        } for listing in listings]
        logger.debug(f"Response data: {response}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error fetching listings: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch listings'}), 500

@marketplace_bp.route('/listings/<int:listing_id>/purchase', methods=['POST'])
@login_required
def purchase_asset(listing_id):
    try:
        user = User.query.get(session['user_id'])
        listing = Listing.query.get_or_404(listing_id)
        asset = listing.asset

        logger.debug(f"Starting purchase of listing {listing_id}")
        logger.debug(f"Listing offer_id: {listing.offer_id}")
        logger.debug(f"Buyer wallet address: {user.xrpl_address}")
        logger.debug(f"Current asset owner_id: {asset.owner_id}")
        logger.debug(f"Asset token_id: {asset.token_id}")

        if listing.status != 'active':
            return jsonify({'error': 'Listing is not active'}), 400

        if listing.seller_id == user.id:
            return jsonify({'error': 'Cannot purchase your own asset'}), 400

        if not asset.is_owned_by(listing.seller_id):
            return jsonify({'error': 'Seller no longer owns this asset'}), 400

        buyer_wallet = Wallet.from_seed(user.xrpl_seed)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            accept_result = loop.run_until_complete(
                accept_buy_offer(
                    buyer_wallet=buyer_wallet,
                    offer_id=listing.offer_id
                )
            )
            logger.debug(f"XRPL offer acceptance successful: {accept_result}")
        finally:
            loop.close()

        try:
            transaction = Transaction(
                listing_id=listing.id,
                buyer_id=user.id,
                seller_id=listing.seller_id,
                price=listing.price,
                xrpl_transaction_hash=accept_result['transaction_hash'],
                status='completed'
            )

            buyer_wallet_tx = WalletTransaction(
                user_id=user.id,
                transaction_type='purchase',
                amount=listing.price,
                status='completed',
                xrpl_transaction_hash=accept_result['transaction_hash']
            )

            seller_wallet_tx = WalletTransaction(
                user_id=listing.seller_id,
                transaction_type='sale',
                amount=listing.price,
                status='completed',
                xrpl_transaction_hash=accept_result['transaction_hash']
            )

            asset.transfer_ownership(user.id, db.session)

            listing.status = 'completed'

            db.session.add_all([transaction, buyer_wallet_tx, seller_wallet_tx])
            db.session.commit()

            logger.info(f"Asset {asset.id} ownership transferred to user {user.id}")
            logger.debug(f"Final asset state - owner_id: {asset.owner_id}, status: {asset.status}")

            return jsonify({
                'message': 'Purchase successful',
                'transaction': {
                    'id': transaction.id,
                    'transaction_hash': accept_result['transaction_hash'],
                    'status': transaction.status,
                    'asset': {
                        'id': asset.id,
                        'token_id': asset.token_id,
                        'owner_id': asset.owner_id,
                        'status': asset.status
                    }
                }
            })

        except Exception as e:
            logger.error(f"Error in ownership transfer or transaction completion: {str(e)}")
            if 'transaction' in locals():
                transaction.status = 'failed'
                db.session.add(transaction)
            db.session.rollback()
            raise Exception(f"Failed to complete purchase: {str(e)}")

    except Exception as e:
        logger.error(f"Error purchasing asset: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/listings/<int:listing_id>/cancel', methods=['POST'])
@login_required
def cancel_listing(listing_id):
    try:
        user = User.query.get(session['user_id'])
        listing = Listing.query.get_or_404(listing_id)

        if listing.seller_id != user.id:
            return jsonify({'error': 'Not authorized to cancel this listing'}), 403

        if listing.status != 'active':
            return jsonify({'error': 'Listing is not active'}), 400

        listing.status = 'cancelled'
        db.session.commit()

        return jsonify({
            'message': 'Listing cancelled successfully'
        })

    except Exception as e:
        logger.error(f"Error cancelling listing: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel listing'}), 500

@marketplace_bp.route('/listings/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    try:
        listing = Listing.query.get_or_404(listing_id)
        return jsonify({
            'id': listing.id,
            'asset': {
                'id': listing.asset.id,
                'title': listing.asset.title,
                'description': listing.asset.description,
                'image_url': listing.asset.image_url,
                'token_id': listing.asset.token_id
            },
            'price': str(listing.price),
            'status': listing.status,
            'seller': {
                'id': listing.seller.id,
                'username': listing.seller.username,
                'xrpl_address': listing.seller.xrpl_address
            },
            'created_at': listing.created_at.isoformat()
        })

    except Exception as e:
        logger.error(f"Error fetching listing {listing_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch listing'}), 500
