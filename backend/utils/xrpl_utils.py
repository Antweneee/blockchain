from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.asyncio.transaction import submit_and_wait as async_submit_and_wait
from xrpl.wallet import Wallet
from xrpl.models.requests import AccountInfo, AccountNFTs
from xrpl.models.transactions import NFTokenMint, NFTokenCreateOffer, NFTokenAcceptOffer, Payment
from xrpl.utils import str_to_hex
import json
import logging
import sys
import requests
import time
from xrpl.clients import JsonRpcClient
from xrpl.asyncio.transaction import autofill_and_sign
from xrpl.models.transactions import Transaction
from xrpl.models.requests import AccountInfo

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

XRPL_NODE = 'https://s.altnet.rippletest.net:51234'
WS_URL = 'wss://s.altnet.rippletest.net:51233'
FAUCET_URL = "https://faucet.altnet.rippletest.net/accounts"
PLATFORM_CREDENTIALS_PATH = '/data/platform-credentials.json'
MAX_RETRIES = 10
RETRY_DELAY = 5

def get_sync_client():
    return JsonRpcClient(XRPL_NODE)

async def get_xrpl_client():
    return AsyncJsonRpcClient(XRPL_NODE)

def wait_for_account_funding(address, max_retries=MAX_RETRIES):
    client = get_sync_client()
    for attempt in range(max_retries):
        try:
            logger.debug(f"Checking funding status for account: {address}")
            acct_info = AccountInfo(
                account=address,
                ledger_index="validated",
                strict=True,
            )
            response = client.request(acct_info)
            logger.debug(f"XRPL AccountInfo response: {json.dumps(response.result, indent=2)}")

            if 'account_data' in response.result:
                balance = response.result['account_data']['Balance']
                logger.debug(f"Account {address} funded with balance: {balance} drops")
                return float(int(balance) / 1000000)
            else:
                logger.debug(f"Account {address} not yet found on XRPL network.")
        except Exception as e:
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries}: Account funding check failed for {address}. Error: {str(e)}"
            )
            time.sleep(RETRY_DELAY)

    return 0.0

def create_xrpl_account():
    try:
        wallet = Wallet.create()
        logger.debug(f"Created wallet with address: {wallet.classic_address}")

        response = requests.post(FAUCET_URL, json={"destination": wallet.classic_address})
        if response.status_code == 200:
            faucet_data = response.json()
            logger.debug(f"Faucet response: {json.dumps(faucet_data, indent=2)}")

            balance = wait_for_account_funding(wallet.classic_address)

            logger.debug(f"Final balance for {wallet.classic_address}: {balance} XRP")
            return {
                'address': wallet.classic_address,
                'seed': wallet.seed,
                'public_key': wallet.public_key,
                'private_key': wallet.private_key,
                'balance': balance
            }
        else:
            logger.error(f"Faucet request failed: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error creating XRPL account: {str(e)}", exc_info=True)
        return None

def get_platform_wallet():
    try:
        with open(PLATFORM_CREDENTIALS_PATH, 'r') as f:
            credentials = json.load(f)
            logger.debug(f"Loaded platform wallet credentials: {json.dumps(credentials, indent=2)}")
            return credentials
    except Exception as e:
        logger.error(f"Error loading platform credentials: {str(e)}")
        return None


def get_account_balance(address):
    try:
        client = get_sync_client()
        acct_info = AccountInfo(
            account=address,
            ledger_index="validated",
            strict=True,
        )
        response = client.request(acct_info)
        logger.debug(f"AccountInfo response for {address}: {json.dumps(response.result, indent=2)}")

        if 'account_data' in response.result:
            balance = response.result['account_data']['Balance']
            logger.debug(f"Retrieved balance for account {address}: {balance} drops")
            return float(int(balance) / 1000000)
        else:
            logger.debug(f"Account {address} not found or not yet funded.")
            return 0.0
    except Exception as e:
        logger.warning(f"Failed to retrieve balance for account {address}: {str(e)}")
        return 0.0

async def mint_nft(wallet, metadata_url, transfer_fee=0):
    try:
        logger.info(f"Starting NFT mint process for wallet: {wallet.classic_address}")

        if not metadata_url.startswith(('http://', 'https://', 'ipfs://')):
            raise ValueError("metadata_url must be a fully qualified URL")

        transfer_fee_bps = int(min(max(transfer_fee, 0), 50) * 100)
        logger.debug(f"Transfer fee (basis points): {transfer_fee_bps}")

        uri_hex = str_to_hex(metadata_url)
        if len(uri_hex) > 256:
            raise ValueError("Metadata URL is too long for XRPL")

        logger.debug(f"URI hex ({len(uri_hex)} chars): {uri_hex}")

        async with AsyncWebsocketClient(WS_URL) as client:
            acct_info = await client.request(AccountInfo(
                account=wallet.classic_address,
                ledger_index="validated"
            ))

            logger.debug(f"Account info: {json.dumps(acct_info.result, indent=2)}")

            sequence = acct_info.result['account_data']['Sequence']
            flags = 8

            mint_tx = NFTokenMint(
                account=wallet.classic_address,
                uri=uri_hex,
                flags=flags,
                fee="12",
                sequence=sequence,
                last_ledger_sequence=None,
                nftoken_taxon=0,
                transfer_fee=transfer_fee_bps
            )

            mint_tx = await autofill_and_sign(mint_tx, client, wallet)
            logger.debug(f"Signed transaction details: {json.dumps(mint_tx.to_dict(), indent=2)}")

            response = await async_submit_and_wait(
                transaction=mint_tx,
                client=client
            )

            logger.debug(f"Submit response: {json.dumps(response.result, indent=2)}")

            if (response.result.get('validated', False) and 
                response.result.get('meta', {}).get('TransactionResult') == 'tesSUCCESS'):

                nft_id = response.result['meta'].get('nftoken_id')
                if not nft_id:
                    raise Exception("NFT ID not found in successful transaction")

                return {
                    'token_id': nft_id,
                    'transaction_hash': response.result['hash']
                }
            else:
                error_msg = response.result.get('meta', {}).get('TransactionResult', 'Unknown error')
                logger.error(f"Minting failed with result: {error_msg}")
                logger.error(f"Full response: {json.dumps(response.result, indent=2)}")
                raise Exception(f"NFT minting failed: {error_msg}")

    except Exception as e:
        logger.error(f"Error minting NFT: {str(e)}", exc_info=True)
        raise

async def submit_transaction(transaction, wallet):
    async with AsyncWebsocketClient(WS_URL) as client:
        signed_tx = await autofill_and_sign(transaction, client, wallet)
        logger.debug(f"Signed transaction: {json.dumps(signed_tx.to_dict(), indent=2)}")

        response = await async_submit_and_wait(signed_tx, client)

        if response.result.get('validated', False) and response.result.get('meta', {}).get('TransactionResult') == 'tesSUCCESS':
            return response
        else:
            error_msg = response.result.get('meta', {}).get('TransactionResult') or 'Unknown error'
            raise Exception(f"Transaction failed: {error_msg}")

async def create_sell_offer(wallet, token_id, price):
    try:
        sell_offer = NFTokenCreateOffer(
            account=wallet.classic_address,
            nftoken_id=token_id,
            amount=str(int(price * 1000000)),
            flags=1
        )

        response = await submit_transaction(sell_offer, wallet)

        offer_id = None
        if 'meta' in response.result and 'AffectedNodes' in response.result['meta']:
            for node in response.result['meta']['AffectedNodes']:
                if 'CreatedNode' in node and node['CreatedNode']['LedgerEntryType'] == 'NFTokenOffer':
                    offer_id = node['CreatedNode']['LedgerIndex']
                    break

        if not offer_id:
            raise Exception("Could not find NFTokenOffer ID in response")

        logger.debug(f"Created NFT offer with ID: {offer_id}")

        return {
            'offer_id': offer_id,
            'transaction_hash': response.result['hash']
        }

    except Exception as e:
        logger.error(f"Error creating sell offer: {str(e)}", exc_info=True)
        raise

async def accept_buy_offer(buyer_wallet, offer_id):
    try:
        logger.debug(f"Accepting offer with ID: {offer_id}")
        logger.debug(f"Buyer address: {buyer_wallet.classic_address}")

        accept_offer = NFTokenAcceptOffer(
            account=buyer_wallet.classic_address,
            nftoken_sell_offer=offer_id
        )

        logger.debug(f"Accept offer transaction: {accept_offer.to_dict()}")
        response = await submit_transaction(accept_offer, buyer_wallet)

        hash = response.result.get('hash') or response.result.get('tx_hash')
        if not hash:
            raise Exception("No transaction hash found in response")

        return {
            'transaction_hash': hash
        }

    except Exception as e:
        logger.error(f"Error accepting offer: {str(e)}")
        raise

