import { Wallet } from 'xrpl'

export class WalletManager {
  constructor() {
    this.wallet = null
  }

  generateWallet() {
    this.wallet = Wallet.generate()
    return {
      address: this.wallet.address,
      seed: this.wallet.seed,
      publicKey: this.wallet.publicKey,
      privateKey: this.wallet.privateKey
    }
  }

  loadWallet(seed) {
    try {
      this.wallet = Wallet.fromSeed(seed)
      return {
        address: this.wallet.address,
        seed: seed,
        publicKey: this.wallet.publicKey,
        privateKey: this.wallet.privateKey
      }
    } catch (error) {
      console.error('Error loading wallet:', error)
      throw new Error('Invalid seed')
    }
  }

  getWallet() {
    if (!this.wallet) {
      throw new Error('No wallet loaded')
    }
    return this.wallet
  }

  getAddress() {
    if (!this.wallet) {
      throw new Error('No wallet loaded')
    }
    return this.wallet.address
  }

  sign(tx) {
    if (!this.wallet) {
      throw new Error('No wallet loaded')
    }
    return this.wallet.sign(tx)
  }

  verifySignature(tx, signature) {
    if (!this.wallet) {
      throw new Error('No wallet loaded')
    }
    return this.wallet.verify(tx, signature)
  }
}

export const walletManager = new WalletManager()
