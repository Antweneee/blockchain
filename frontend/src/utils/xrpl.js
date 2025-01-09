import { Client, NFTokenMint, NFTokenCreateOffer, Payment } from 'xrpl'

const XRPL_NODE = import.meta.env.VITE_XRPL_NODE || 'wss://s.altnet.rippletest.net:51233'

class XRPLService {
  constructor() {
    this.client = new Client(XRPL_NODE)
    this.connected = false
  }

  async ensureConnection() {
    if (!this.connected) {
      await this.client.connect()
      this.connected = true
    }
  }

  async disconnect() {
    if (this.connected) {
      await this.client.disconnect()
      this.connected = false
    }
  }

  async mintNFT(wallet, tokenURI, transferFee = 0) {
    try {
      await this.ensureConnection()

      const transactionBlob = {
        TransactionType: "NFTokenMint",
        Account: wallet.address,
        URI: Buffer.from(tokenURI, 'utf8').toString('hex').toUpperCase(),
        NFTokenTaxon: 0,
        Flags: transferFee > 0 ? NFTokenMint.tfTransferable : 0,
        TransferFee: transferFee * 1000
      }

      const tx = await this.client.submitAndWait(transactionBlob, {
        wallet: wallet
      })

      const nfts = await this.client.request({
        command: "account_nfts",
        account: wallet.address
      })

      return {
        tokenId: nfts.result.account_nfts[nfts.result.account_nfts.length - 1].NFTokenID,
        hash: tx.result.hash
      }
    } catch (error) {
      console.error('Error minting NFT:', error)
      throw error
    }
  }

  async createSellOffer(wallet, tokenId, amount) {
    try {
      await this.ensureConnection()

      const transactionBlob = {
        TransactionType: "NFTokenCreateOffer",
        Account: wallet.address,
        NFTokenID: tokenId,
        Amount: this.xrpToDrops(amount),
        Flags: NFTokenCreateOffer.tfSellToken
      }

      const tx = await this.client.submitAndWait(transactionBlob, {
        wallet: wallet
      })

      return {
        offerIndex: tx.result.hash,
        hash: tx.result.hash
      }
    } catch (error) {
      console.error('Error creating sell offer:', error)
      throw error
    }
  }

  async acceptBuyOffer(wallet, offerIndex) {
    try {
      await this.ensureConnection()

      const transactionBlob = {
        TransactionType: "NFTokenAcceptOffer",
        Account: wallet.address,
        NFTokenBuyOffer: offerIndex
      }

      const tx = await this.client.submitAndWait(transactionBlob, {
        wallet: wallet
      })

      return {
        hash: tx.result.hash
      }
    } catch (error) {
      console.error('Error accepting buy offer:', error)
      throw error
    }
  }

  async getAccountInfo(address) {
    try {
      await this.ensureConnection()

      const response = await this.client.request({
        command: 'account_info',
        account: address,
        ledger_index: 'validated'
      })

      return {
        balance: this.dropsToXRP(response.result.account_data.Balance),
        sequence: response.result.account_data.Sequence
      }
    } catch (error) {
      console.error('Error getting account info:', error)
      throw error
    }
  }

  async getAccountNFTs(address) {
    try {
      await this.ensureConnection()

      const response = await this.client.request({
        command: 'account_nfts',
        account: address
      })

      return response.result.account_nfts
    } catch (error) {
      console.error('Error getting account NFTs:', error)
      throw error
    }
  }

  async sendPayment(wallet, destination, amount) {
    try {
      await this.ensureConnection()

      const transactionBlob = {
        TransactionType: "Payment",
        Account: wallet.address,
        Destination: destination,
        Amount: this.xrpToDrops(amount)
      }

      const tx = await this.client.submitAndWait(transactionBlob, {
        wallet: wallet
      })

      return {
        hash: tx.result.hash
      }
    } catch (error) {
      console.error('Error sending payment:', error)
      throw error
    }
  }

  xrpToDrops(xrp) {
    return Math.floor(xrp * 1000000).toString()
  }

  dropsToXRP(drops) {
    return parseFloat(drops) / 1000000
  }
}

export const xrplService = new XRPLService()

export const XRPL_EXPLORER_URL = 'https://testnet.xrpl.org/transactions/'
