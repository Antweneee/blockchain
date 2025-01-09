<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-medium text-gray-900">My Assets</h3>
        <p class="mt-2 text-3xl font-semibold text-primary">{{ userAssets.length }}</p>
        <p class="text-sm text-gray-500">Total tokenized assets</p>
      </div>
      
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-medium text-gray-900">Active Listings</h3>
        <p class="mt-2 text-3xl font-semibold text-primary">{{ activeListings.length }}</p>
        <p class="text-sm text-gray-500">Assets listed for sale</p>
      </div>
      
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-medium text-gray-900">XRP Balance</h3>
        <p class="mt-2 text-3xl font-semibold text-primary">{{ walletStore.balance }} XRP</p>
        <p class="text-sm text-gray-500">Available balance</p>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="bg-white rounded-lg shadow-sm p-6 mb-8">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-medium text-gray-900">Recent Activity</h2>
        <router-link to="/wallet" class="text-primary hover:text-secondary text-sm">
          View all transactions
        </router-link>
      </div>
      
      <div class="space-y-4">
        <div v-for="tx in recentTransactions" :key="tx.id" 
             class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div class="flex items-center space-x-4">
            <div :class="[
              'w-10 h-10 rounded-full flex items-center justify-center',
              tx.type === 'deposit' ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600'
            ]">
              <span v-if="tx.type === 'deposit'">↓</span>
              <span v-else>↑</span>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">
                {{ tx.type === 'deposit' ? 'Deposit' : 'Purchase' }}
              </p>
              <p class="text-sm text-gray-500">{{ formatDate(tx.created_at) }}</p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-sm font-medium text-gray-900">{{ tx.amount }} XRP</p>
            <p class="text-xs text-gray-500 truncate w-32" :title="tx.xrpl_transaction_hash">
              {{ truncateHash(tx.xrpl_transaction_hash) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- My Assets -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-medium text-gray-900">My Assets</h2>
        <router-link to="/tokenize" class="btn-primary">
          Tokenize New Asset
        </router-link>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AssetCard
          v-for="asset in userAssets"
          :key="asset.id"
          :asset="asset"
          :listing="getListingForAsset(asset.id)"
        />
      </div>
      
      <div v-if="userAssets.length === 0" class="text-center py-8">
        <p class="text-gray-500">You haven't tokenized any assets yet</p>
        <router-link to="/tokenize" class="text-primary hover:text-secondary">
          Get started by tokenizing your first asset
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMarketplaceStore, useWalletStore, useAuthStore } from '../store'
import AssetCard from '../components/AssetCard.vue'

const marketplaceStore = useMarketplaceStore()
const walletStore = useWalletStore()
const authStore = useAuthStore()

onMounted(async () => {
  try {
    await Promise.all([
      marketplaceStore.fetchMyAssets(),
      marketplaceStore.fetchListings(),
      walletStore.fetchTransactions(),
      walletStore.fetchBalance()
    ]);
    console.log('Dashboard initialized. Wallet balance:', walletStore.balance);
  } catch (error) {
    console.error('Error initializing dashboard:', error);
  }
});


const userAssets = computed(() => marketplaceStore.myAssets)

const activeListings = computed(() => {
  console.log('Checking active listings:', marketplaceStore.listings)
  return marketplaceStore.listings.filter(listing => {
    console.log(`Listing ${listing.id}: Status=${listing.status}, Seller=${listing.seller_id}, User=${authStore.user?.id}`)
    return listing.seller_id === authStore.user?.id && listing.status === 'active'
  })
})

const recentTransactions = computed(() => {
  console.log('Wallet transactions:', walletStore.transactions);
  return walletStore.transactions
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5);
})

const getListingForAsset = (assetId) => {
  return marketplaceStore.listings.find(listing => listing.asset_id === assetId)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const truncateHash = (hash) => {
  if (!hash) return ''
  return `${hash.slice(0, 6)}...${hash.slice(-4)}`
}
</script>
