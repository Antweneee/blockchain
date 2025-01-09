<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div v-if="asset" class="bg-white rounded-lg shadow-sm">
      <!-- Asset Header -->
      <div class="relative h-96">
        <img 
          :src="asset.image_url" 
          :alt="asset.title"
          class="w-full h-full object-cover rounded-t-lg"
        >
        <div class="absolute top-4 left-4">
          <button 
            @click="router.back()" 
            class="bg-white p-2 rounded-full shadow-md hover:bg-gray-50"
          >
            ← Back
          </button>
        </div>
      </div>

      <div class="p-6">
        <div class="flex justify-between items-start">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">{{ asset.title }}</h1>
            <p class="text-sm text-gray-500">Owned by {{ asset.owner }}</p>
          </div>
          <div v-if="currentListing" class="text-right">
            <p class="text-lg font-medium text-primary">{{ currentListing.price }} XRP</p>
            <p class="text-sm text-gray-500">Current price</p>
          </div>
        </div>

        <div class="mt-6 border-t border-gray-200 pt-6">
          <h2 class="text-lg font-medium text-gray-900">Token Details</h2>
          <dl class="mt-4 grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt class="text-sm font-medium text-gray-500">Token ID</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ asset.token_id }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Status</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ asset.status }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Created At</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ formatDate(asset.created_at) }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ formatDate(asset.updated_at) }}</dd>
            </div>
          </dl>
        </div>

        <div class="mt-6 border-t border-gray-200 pt-6">
          <h2 class="text-lg font-medium text-gray-900">Description</h2>
          <p class="mt-4 text-gray-600 whitespace-pre-line">{{ asset.description }}</p>
        </div>

        <div class="mt-6 border-t border-gray-200 pt-6 flex justify-end space-x-4">
          <template v-if="isOwner">
            <button 
              v-if="!currentListing"
              @click="showListingModal = true"
              class="btn-primary"
            >
              List for Sale
            </button>
            <button 
              v-else
              @click="cancelListing"
              class="btn-secondary"
            >
              Cancel Listing
            </button>
          </template>
          <button 
            v-else-if="currentListing"
            @click="showPurchaseModal = true"
            class="btn-primary"
          >
            Purchase Now
          </button>
        </div>
      </div>
    </div>

    <div v-else-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
    </div>

    <div v-if="showListingModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-medium text-gray-900 mb-4">List Asset for Sale</h3>
        <form @submit.prevent="createListing">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700">Price (XRP)</label>
            <input 
              v-model="listingPrice"
              type="number"
              step="0.000001"
              min="0"
              required
              class="input-field"
            >
          </div>
          <div class="flex justify-end space-x-4">
            <button 
              type="button"
              @click="showListingModal = false"
              class="btn-secondary"
            >
              Cancel
            </button>
            <button 
              type="submit"
              class="btn-primary"
            >
              Create Listing
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showPurchaseModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Confirm Purchase</h3>
        <p class="text-sm text-gray-600 mb-4">
          Are you sure you want to purchase this asset for {{ currentListing?.price }} XRP?
        </p>
        <div class="flex justify-end space-x-4">
          <button 
            @click="showPurchaseModal = false"
            class="btn-secondary"
          >
            Cancel
          </button>
          <button 
            @click="confirmPurchase"
            class="btn-primary"
          >
            Confirm Purchase
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMarketplaceStore, useAuthStore } from '../store'

const router = useRouter()
const route = useRoute()
const marketplaceStore = useMarketplaceStore()
const authStore = useAuthStore()

const loading = ref(true)
const showListingModal = ref(false)
const showPurchaseModal = ref(false)
const listingPrice = ref('')

const asset = computed(() => {
  const foundAsset = marketplaceStore.assets.find(a => a.id === parseInt(route.params.id))
  if (foundAsset) {
    return {
      ...foundAsset,
      owner: foundAsset.owner.username
    }
  }
  return null
})

const currentListing = computed(() => 
  marketplaceStore.listings.find(l => l.asset_id === asset.value?.id && l.status === 'active')
)

const isOwner = computed(() => 
  asset.value?.owner_id === authStore.user?.id
)

onMounted(async () => {
  try {
    await Promise.all([
      marketplaceStore.fetchAssets(),
      marketplaceStore.fetchListings()
    ])
  } finally {
    loading.value = false
  }
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const createListing = async () => {
  try {
    await marketplaceStore.createListing({
      asset_id: asset.value.id,
      price: parseFloat(listingPrice.value)
    })
    showListingModal.value = false
    await marketplaceStore.fetchListings()
  } catch (error) {
    console.error('Failed to create listing:', error)
  }
}

const cancelListing = async () => {
  try {
    await marketplaceStore.cancelListing(currentListing.value.id)
    await marketplaceStore.fetchListings()
  } catch (error) {
    console.error('Failed to cancel listing:', error)
  }
}

const confirmPurchase = async () => {
  try {
    await marketplaceStore.purchaseAsset(currentListing.value.id)
    showPurchaseModal.value = false
    await Promise.all([
      marketplaceStore.fetchAssets(),
      marketplaceStore.fetchListings()
    ])
  } catch (error) {
    console.error('Failed to purchase asset:', error)
  }
}
</script>
