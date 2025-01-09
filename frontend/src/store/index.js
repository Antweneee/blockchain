import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'https://cryptoplace.kusmicrew.cloud/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    error: null,
    loading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
  },

  actions: {
    init() {
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        this.user = JSON.parse(storedUser)
      }
    },

    async login(credentials) {
      try {
        this.loading = true
        this.error = null
        const response = await axios.post(`${API_URL}/auth/login`, credentials)
        this.user = response.data.user
        localStorage.setItem('user', JSON.stringify(response.data.user))
        return response.data
      } catch (error) {
        console.error('Login error:', error)
        this.error = error.response?.data?.error || 'Login failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        await axios.post(`${API_URL}/auth/logout`)
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.user = null
        localStorage.removeItem('user')
      }
    }
  }
})

export const useMarketplaceStore = defineStore('marketplace', {
  state: () => ({
    assets: [],
    myAssets : [],
    listings: [],
    loading: false,
  }),
  actions: {
    async createAsset(data) {
      try {
        const response = await axios.post(`${API_URL}/assets`, data)
        return response.data
      } catch (error) {
        console.error('Error creating asset:', error)
        throw error.response?.data?.error || 'Asset creation failed'
      }
    },
    async createListing(data) {
      try {
        const response = await axios.post(`${API_URL}/marketplace/listings`, data)
        return response.data
      } catch (error) {
        console.error('Error creating listing:', error)
        throw error.response?.data?.error || 'Listing creation failed'
      }
    },
    async cancelListing(listingId) {
      try {
        const response = await axios.post(`${API_URL}/marketplace/listings/${listingId}/cancel`)
        await this.fetchListings()
        return response.data
      } catch (error) {
        console.error('Error cancelling listing:', error)
        throw error.response?.data?.error || 'Cancellation failed'
      }
    },
    async fetchAssets() {
      try {
        this.loading = true
        const response = await axios.get(`${API_URL}/assets`)
        this.assets = response.data
      } catch (error) {
        console.error('Error fetching assets:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchMyAssets() {
      try {
        this.loading = true
        const user = JSON.parse(localStorage.getItem('user'))
        if (!user) throw new Error('No user logged in')
        const response = await axios.get(`${API_URL}/assets?owner_id=${user.id}`)
        this.myAssets = response.data
      } catch (error) {
        console.error('Error fetching my assets:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    async purchaseAsset(listingId) {
      try {
        const response = await axios.post(`${API_URL}/marketplace/listings/${listingId}/purchase`)
        await this.fetchListings()
        return response.data
      } catch (error) {
        console.error('Error purchasing asset:', error)
        throw error.response?.data?.error || 'Purchase failed'
      }
    },
    async fetchListings() {
      try {
        this.loading = true
        const response = await axios.get(`${API_URL}/marketplace/listings`)
        this.listings = response.data
      } catch (error) {
        console.error('Error fetching listings:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})


export const useWalletStore = defineStore('wallet', {
  state: () => ({
    transactions: [],
    balance: 0,
  }),
  actions: {
    async fetchTransactions() {
      try {
        console.log('Fetching transactions...');
        const response = await axios.get(`${API_URL}/wallet/transactions`);
        this.transactions = response.data;
        console.log('Fetched transactions:', this.transactions);
      } catch (error) {
        console.error('Error fetching transactions:', error);
        throw error;
      }
    },

    async fetchBalance() {
      try {
        console.log('Fetching wallet balance...');
        const response = await axios.get(`${API_URL}/wallet/balance`);
        this.balance = parseFloat(response.data.balance);
        console.log('Updated wallet balance:', this.balance);
      } catch (error) {
        console.error('Error fetching balance:', error);
        throw error;
      }
    },

    async createDeposit(data) {
      try {
        const response = await axios.post(`${API_URL}/wallet/deposit`, data);
        await this.fetchTransactions();
        await this.fetchBalance();
        return response.data;
      } catch (error) {
        console.error('Error creating deposit:', error);
        throw error.response?.data?.error || 'Deposit failed';
      }
    },
  },
});
