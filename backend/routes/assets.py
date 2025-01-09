from flask import Blueprint, request, jsonify, session
from models import db, Asset, User
from utils.auth import login_required
from utils.xrpl_utils import mint_nft, get_xrpl_client
from xrpl.wallet import Wallet
import logging
import asyncio
import sys
import json
import os

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

assets_bp = Blueprint('assets', __name__)


@assets_bp.route('', methods=['POST'])
@assets_bp.route('/', methods=['POST'])
@login_required
def create_asset():
    try:
        logger.info("Starting asset creation process")
        data = request.get_json()
        logger.debug(f"Received data: {json.dumps(data, indent=2)}")

        user = User.query.get(session['user_id'])
        logger.debug(f"User details: ID={user.id}, XRPL Address={user.xrpl_address}")

        wallet = Wallet.from_seed(user.xrpl_seed)
        logger.debug(f"Created wallet with address: {wallet.classic_address}")

        if wallet.classic_address != user.xrpl_address:
            raise Exception("Wallet address mismatch with stored user address")

        async def async_mint():
            return await mint_nft(
                wallet=wallet,
                metadata_url=data['metadata_url'],
                transfer_fee=data.get('transfer_fee', 0)
            )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            nft_result = loop.run_until_complete(async_mint())
        finally:
            loop.close()

        logger.debug(f"NFT creation result: {json.dumps(nft_result, indent=2)}")

        metadata_path = data['metadata_url'].replace(
            'https://cryptoplace.kusmicrew.cloud/api/uploads/', ''
        )
        try:
            full_path = os.path.join('/data/uploads', metadata_path)
            logger.debug(f"Reading metadata from: {full_path}")
            with open(full_path) as f:
                metadata = json.load(f)
                image_url = metadata.get('image', '')
        except Exception as e:
            logger.error(f"Error reading metadata file: {str(e)}")
            image_url = ""

        asset = Asset(
            owner_id=user.id,
            title=data['title'],
            description=data['description'],
            image_url=image_url,
            status='active',
            token_id=nft_result['token_id']
        )

        db.session.add(asset)
        db.session.commit()
        logger.info(f"Asset created successfully with ID: {asset.id}")

        return jsonify({
            'message': 'Asset created successfully',
            'asset': {
                'id': asset.id,
                'title': asset.title,
                'token_id': asset.token_id,
                'transaction_hash': nft_result['transaction_hash']
            }
        }), 201

    except KeyError as e:
        logger.error(f"Missing required field: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error creating asset: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assets_bp.route('', methods=['GET'])
@assets_bp.route('/', methods=['GET'])
def get_assets():
    try:
        owner_id = request.args.get('owner_id')

        query = Asset.query.filter(Asset.status.in_(['active', 'listed']))

        if owner_id:
            query = query.filter_by(owner_id=owner_id)

        assets = query.all()
        return jsonify([{
            'id': asset.id,
            'title': asset.title,
            'description': asset.description,
            'image_url': asset.image_url,
            'token_id': asset.token_id,
            'status': asset.status,
            'owner': {
                'id': asset.owner.id,
                'username': asset.owner.username
            },
            'owner_id': asset.owner_id,
            'created_at': asset.created_at.isoformat(),
            'updated_at': asset.updated_at.isoformat()
        } for asset in assets])

    except Exception as e:
        logger.error(f"Error fetching assets: {str(e)}")
        return jsonify({'error': 'Failed to fetch assets'}), 500

@assets_bp.route('/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    try:
        asset = Asset.query.get_or_404(asset_id)

        active_listing = next((listing for listing in asset.listings 
                             if listing.status == 'active'), None)
        response = {
            'id': asset.id,
            'title': asset.title,
            'description': asset.description,
            'image_url': asset.image_url,
            'token_id': asset.token_id,
            'status': asset.status,
            'owner': {
                'id': asset.owner.id,
                'username': asset.owner.username
            },
            'owner_id': asset.owner_id,
            'created_at': asset.created_at.isoformat(),
            'updated_at': asset.updated_at.isoformat(),
            'listing': None
        }

        if active_listing:
            response['listing'] = {
                'id': active_listing.id,
                'price': str(active_listing.price),
                'status': active_listing.status,
                'offer_id': active_listing.offer_id
            }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error fetching asset {asset_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch asset'}), 500
