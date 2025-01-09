<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Profile Overview -->
    <div class="bg-white rounded-lg shadow-sm p-6 mb-8">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">My Profile</h1>
          <p class="text-sm text-gray-500 mt-1">Manage your account settings and view your activity</p>
        </div>
        <button
          @click="logout"
          class="text-red-600 hover:text-red-700 font-medium"
        >
          Sign Out
        </button>
      </div>

      <!-- User Information -->
      <div class="mt-6 grid grid-cols-1 gap-y-6 sm:grid-cols-2 gap-x-4">
        <div>
          <h3 class="text-sm font-medium text-gray-500">Username</h3>
          <p class="mt-1 text-sm text-gray-900">{{ authStore.user?.username }}</p>
        </div>

        <div>
          <h3 class="text-sm font-medium text-gray-500">Email</h3>
          <p class="mt-1 text-sm text-gray-900">{{ authStore.user?.email }}</p>
        </div>

        <div>
          <h3 class="text-sm font-medium text-gray-500">Member Since</h3>
          <p class="mt-1 text-sm text-gray-900">{{ formatDate(authStore.user?.created_at) }}</p>
        </div>

        <div>
          <h3 class="text-sm font-medium text-gray-500">XRPL Address</h3>
          <p class="mt-1 text-sm font-mono break-all text-gray-900">{{ authStore.user?.xrpl_address }}</p>
        </div>
      </div>

      <!-- Edit Profile Button -->
      <div class="mt-6 border-t border-gray-200 pt-6">
        <button
          @click="showEditModal = true"
          class="btn-primary"
        >
          Edit Profile
        </button>
      </div>
    </div>

    <!-- Activity Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-medium text-gray-900">Assets Owned</h3>
        <p class="mt-2 text-3xl font-semibold text-primary">{{ userAssets.length }}</p>
        <p class="text-sm text-gray-500">{{ userAssets.length === 1 ? 'Asset' : 'Assets' }} in your collection</p>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-medium text-gray-900">Active Listings</h3>
        <p class="mt-2 text-3xl font-semibold text-primary">{{ activeListings.length }}</p>
        <p class="text-sm text-gray-500">
          Assets currently for sale
          <span v-if="activeListings.length > 0" class="block mt-1">
            Total value: {{ getTotalListingsValue() }} XRP
          </span>
        </p>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-medium text-gray-900">Total Transactions</h3>
        <p class="mt-2 text-3xl font-semibold text-primary">{{ walletStore.transactions.length }}</p>
        <p class="text-sm text-gray-500">Transaction history</p>
      </div>
    </div>

    <!-- Assets Overview -->
    <div class="bg-white rounded-lg shadow-sm p-6 mb-8">
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

    <!-- Active Listings -->
    <div class="bg-white rounded-lg shadow-sm p-6 mb-8">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Active Listings</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AssetCard
          v-for="listing in activeListings"
          :key="listing.id"
          :asset="listing.asset"
          :listing="listing"
        />
      </div>

      <div v-if="activeListings.length === 0" class="text-center py-8">
        <p class="text-gray-500">No active listings</p>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-6">Recent Activity</h2>

      <div class="space-y-4">
        <div v-for="activity in recentActivity" :key="activity.id"
             class="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
          <div class="flex items-center space-x-4">
            <div :class="[
              'w-10 h-10 rounded-full flex items-center justify-center',
              getActivityColor(activity.type)
            ]">
              {{ getActivityIcon(activity.type) }}
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ activity.description }}</p>
              <div class="flex items-center space-x-2">
                <p class="text-xs text-gray-500">{{ formatDate(activity.date) }}</p>
                <span v-if="activity.status"
                      :class="[
                        'px-2 py-0.5 rounded-full text-xs',
                        {
                          'bg-green-100 text-green-800': activity.status === 'completed' || activity.status === 'active',
                          'bg-yellow-100 text-yellow-800': activity.status === 'pending',
                          'bg-red-100 text-red-800': activity.status === 'cancelled' || activity.status === 'failed'
                        }
                      ]"
                >
                  {{ activity.status }}
                </span>
              </div>
            </div>
          </div>
          <div class="text-sm text-gray-500">
            <span :class="{
              'text-red-600': activity.type === 'purchase',
              'text-green-600': activity.type === 'sale' || activity.type === 'deposit'
            }">
              {{ activity.details }}
            </span>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="recentActivity.length === 0" class="text-center py-8">
          <p class="text-gray-500">No recent activity</p>
          <router-link to="/tokenize" class="text-primary hover:text-secondary mt-2 inline-block">
            Get started by tokenizing your first asset
          </router-link>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Edit Profile</h3>

        <form @submit.prevent="updateProfile" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Username</label>
            <input
              v-model="editForm.username"
              type="text"
              required
              class="input-field"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Email</label>
            <input
              v-model="editForm.email"
              type="email"
              required
              class="input-field"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">New Password (optional)</label>
            <input
              v-model="editForm.password"
              type="password"
              class="input-field"
            >
          </div>

          <div class="flex justify-end space-x-4">
            <button
              type="button"
              @click="showEditModal = false"
              class="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn-primary"
              :disabled="updating"
            >
              {{ updating ? 'Updating...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, useMarketplaceStore, useWalletStore } from '../store'
import AssetCard from '../components/AssetCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const marketplaceStore = useMarketplaceStore()
const walletStore = useWalletStore()

const showEditModal = ref(false)
const updating = ref(false)

const editForm = ref({
  username: authStore.user?.username || '',
  email: authStore.user?.email || '',
  password: ''
})

onMounted(async () => {
  try {
    await Promise.all([
      marketplaceStore.fetchMyAssets(),
      marketplaceStore.fetchListings(),
      walletStore.fetchTransactions()
    ])
    console.log('Profile data loaded:', {
      assets: marketplaceStore.assets,
      listings: marketplaceStore.listings,
      transactions: walletStore.transactions
    })
  } catch (error) {
    console.error('Error initializing profile view:', error)
  }
})

const userAssets = computed(() => marketplaceStore.myAssets)

const activeListings = computed(() => {
  console.log('Current listings:', marketplaceStore.listings)
  return marketplaceStore.listings.filter(listing => {
    const isUserListing = listing.seller_id === authStore.user?.id
    const isActive = listing.status === 'active'
    console.log(`Listing ${listing.id}: User=${isUserListing}, Active=${isActive}`)
    return isUserListing && isActive
  })
})

const getTotalListingsValue = () => {
  return activeListings.value
    .reduce((total, listing) => total + Number(listing.price), 0)
    .toFixed(2)
}

const getListingForAsset = (assetId) => {
  return marketplaceStore.listings.find(listing => 
    listing.asset_id === assetId && listing.status === 'active'
  )
}

const recentActivity = computed(() => {
  const activities = []

  userAssets.value.forEach(asset => {
    activities.push({
      id: `asset-${asset.id}`,
      type: 'asset',
      date: asset.created_at,
      description: `Created asset "${asset.title}"`,
      details: asset.status
    })
  })

  marketplaceStore.listings
    .filter(listing => listing.seller_id === authStore.user?.id)
    .forEach(listing => {
      activities.push({
        id: `listing-${listing.id}`,
        type: 'listing',
        date: listing.created_at,
        description: `Listed "${listing.asset.title}" for sale`,
        details: `${listing.price} XRP`,
        status: listing.status
      })
    })

  walletStore.transactions.forEach(tx => {
    activities.push({
      id: `tx-${tx.id}`,
      type: tx.transaction_type,
      date: tx.created_at,
      description: tx.transaction_type === 'deposit' ? 'XRP Deposit' : 'XRP Purchase',
      details: `${tx.amount} XRP`
    })
  })

  return activities
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 10)
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getActivityColor = (type) => {
  switch (type) {
    case 'asset':
      return 'bg-purple-100 text-purple-600'
    case 'listing':
      return 'bg-blue-100 text-blue-600'
    case 'deposit':
      return 'bg-green-100 text-green-600'
    case 'purchase':
      return 'bg-red-100 text-red-600'
    case 'sale':
      return 'bg-green-100 text-green-600'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

const getActivityIcon = (type) => {
  switch (type) {
    case 'asset':
      return '🖼'
    case 'listing':
      return '💰'
    case 'deposit':
      return '↓'
    case 'purchase':
      return '↑'
    case 'sale':
      return '💵'
    default:
      return '•'
  }
}

const updateProfile = async () => {
  if (updating.value) return

  try {
    updating.value = true
    await authStore.updateProfile(editForm.value)
    showEditModal.value = false
  } catch (error) {
    console.error('Failed to update profile:', error)
  } finally {
    updating.value = false
  }
}

const logout = async () => {
  await authStore.logout()
  router.push('/landing')
}
</script>
