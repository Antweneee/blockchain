<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Asset Marketplace</h1>
      <router-link to="/tokenize" class="btn-primary">
        Tokenize New Asset
      </router-link>
    </div>

    <!-- Filters -->
    <div class="mb-8 bg-white p-4 rounded-lg shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Sort by</label>
          <select v-model="sortBy" class="input-field">
            <option value="recent">Most Recent</option>
            <option value="price-low">Price: Low to High</option>
            <option value="price-high">Price: High to Low</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Status</label>
          <select v-model="statusFilter" class="input-field">
            <option value="all">All Listings</option>
            <option value="active">Active Listings</option>
            <option value="sold">Sold Listings</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Search</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search assets..."
            class="input-field"
          >
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="marketplaceStore.loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
    </div>

    <!-- Asset grid -->
    <div v-else-if="filteredListings.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="listing in filteredListings"
        :key="listing.id"
        class="bg-white rounded-xl shadow-md overflow-hidden"
      >
        <div class="relative">
          <img
            :src="listing.asset.image_url"
            :alt="listing.asset.title"
            class="h-48 w-full object-cover"
          >
          <div
            v-if="listing.status === 'sold'"
            class="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded-md text-sm"
          >
            Sold
          </div>
        </div>

        <div class="p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ listing.asset.title }}</h3>
          <p class="text-sm text-gray-600 mb-3 line-clamp-2">{{ listing.asset.description }}</p>

          <div class="flex justify-between items-center">
            <div class="flex items-center space-x-1">
              <span class="text-sm text-gray-500">Seller:</span>
              <span class="text-sm font-medium text-gray-900">{{ listing.seller.username }}</span>
            </div>
            <div class="flex items-center space-x-1">
              <span class="text-sm font-medium text-primary">{{ listing.price }} XRP</span>
            </div>
          </div>

          <div class="mt-4 flex space-x-2">
            <router-link
              :to="{ name: 'asset-details', params: { id: listing.asset.id }}"
              class="flex-1 bg-primary text-white text-center py-2 px-4 rounded-md"
            >
              View Details
            </router-link>
            
            <button v-if="isOwner(listing)"
              @click="cancelListing(listing.id)"
              class="flex-1 bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600"
            >
              Cancel
            </button>
            
            <button v-else-if="listing.status === 'active'"
              @click="handlePurchase(listing)"
              class="flex-1 bg-accent text-white py-2 px-4 rounded-md"
              :disabled="isPurchasing"
            >
              {{ isPurchasing ? 'Processing...' : 'Purchase' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!marketplaceStore.loading" class="text-center py-12">
      <p class="text-gray-500">No listings found matching your criteria</p>
    </div>

    <!-- Purchase confirmation modal -->
    <div v-if="selectedListing" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Confirm Purchase</h3>
        <p class="text-sm text-gray-600 mb-4">
          Are you sure you want to purchase "{{ selectedListing.asset.title }}" for {{ selectedListing.price }} XRP?
        </p>
        <div class="flex justify-end space-x-4">
          <button
            @click="selectedListing = null"
            class="btn-secondary"
          >
            Cancel
          </button>
          <button
            @click="confirmPurchase"
            class="btn-primary"
            :disabled="isPurchasing"
          >
            {{ isPurchasing ? 'Processing...' : 'Confirm Purchase' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Transaction progress modal -->
    <div v-if="showProgress" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Processing Purchase</h3>
        <div class="space-y-4">
          <div v-for="(step, index) in progressSteps" :key="index" class="flex items-center">
            <div :class="[
              'flex-shrink-0 h-6 w-6 rounded-full flex items-center justify-center',
              step.completed ? 'bg-green-100 text-green-600' :
              step.current ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'
            ]">
              <span v-if="step.completed">✓</span>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span class="ml-3 text-sm text-gray-600">{{ step.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMarketplaceStore, useAuthStore, useWalletStore } from '../store'
import { useRouter } from 'vue-router'

const router = useRouter()
const marketplaceStore = useMarketplaceStore()
const authStore = useAuthStore()
const walletStore = useWalletStore()

const sortBy = ref('recent')
const statusFilter = ref('all')
const searchQuery = ref('')
const selectedListing = ref(null)
const isPurchasing = ref(false)
const showProgress = ref(false)

const progressSteps = ref([
  { label: 'Accepting NFT offer', completed: false, current: false },
  { label: 'Processing payment', completed: false, current: false },
  { label: 'Updating ownership', completed: false, current: false }
])

onMounted(async () => {
  try {
    console.log('Fetching listings...')
    await marketplaceStore.fetchListings()
    console.log('Listings data:', marketplaceStore.listings)
  } catch (error) {
    console.error('Error in MarketplaceView:', error)
  }
})

const filteredListings = computed(() => {
  let listings = [...marketplaceStore.listings]
  console.log('Raw listings:', listings)

  if (statusFilter.value !== 'all') {
    console.log('Filtering by status:', statusFilter.value.toLowerCase())
    console.log('Before filter:', listings.map(l => `ID: ${l.id}, Status: ${l.status}`))
    
    listings = listings.filter(listing => {
      console.log(`Comparing listing ${listing.id}: ${listing.status} with ${statusFilter.value.toLowerCase()}`)
      return listing.status === statusFilter.value.toLowerCase()
    })
    
    console.log('After filter:', listings.map(l => `ID: ${l.id}, Status: ${l.status}`))
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    listings = listings.filter(listing =>
      listing.asset.title.toLowerCase().includes(query) ||
      listing.asset.description.toLowerCase().includes(query)
    )
  }

  switch (sortBy.value) {
    case 'price-low':
      listings.sort((a, b) => parseFloat(a.price) - parseFloat(b.price))
      break
    case 'price-high':
      listings.sort((a, b) => parseFloat(b.price) - parseFloat(a.price))
      break
    case 'recent':
    default:
      listings.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }

  console.log('Filtered listings:', listings)
  return listings
})

const isOwner = (listing) => {
  return listing.seller.id === authStore.user?.id
}

const handlePurchase = (listing) => {
  selectedListing.value = listing
}

const cancelListing = async (listingId) => {
  try {
    await marketplaceStore.cancelListing(listingId)
    await marketplaceStore.fetchListings()
  } catch (error) {
    console.error('Error cancelling listing:', error)
  }
}

const confirmPurchase = async () => {
  if (!selectedListing.value || isPurchasing.value) return

  try {
    isPurchasing.value = true
    showProgress.value = true
    progressSteps.value[0].current = true

    await marketplaceStore.purchaseAsset(selectedListing.value.id)

    progressSteps.value[0].completed = true
    progressSteps.value[1].current = true

    await walletStore.fetchBalance()

    progressSteps.value[1].completed = true
    progressSteps.value[2].current = true

    await marketplaceStore.fetchListings()

    progressSteps.value[2].completed = true

    router.push(`/asset-details/${selectedListing.value.asset.id}`)
  } catch (error) {
    console.error('Purchase failed:', error)
  } finally {
    isPurchasing.value = false
    showProgress.value = false
    selectedListing.value = null

    progressSteps.value.forEach(step => {
      step.completed = false
      step.current = false
    })
  }
}
</script>
