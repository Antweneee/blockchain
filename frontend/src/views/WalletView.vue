<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Wallet Overview -->
    <div class="bg-white rounded-lg shadow-sm p-6 mb-8">
      <div class="flex justify-between items-start">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">XRPL Wallet</h1>
          <p class="text-sm text-gray-500 mt-1">Manage your XRP and tokenized assets</p>
        </div>
        <button
          @click="showDepositModal = true"
          class="btn-primary"
        >
          Deposit XRP
        </button>
      </div>

      <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-gray-50 p-4 rounded-lg">
          <h3 class="text-sm font-medium text-gray-500">Available Balance</h3>
          <p class="mt-2 text-3xl font-semibold text-primary">{{ walletStore.balance }} XRP</p>
        </div>

        <div class="bg-gray-50 p-4 rounded-lg">
          <h3 class="text-sm font-medium text-gray-500">XRPL Address</h3>
          <p class="mt-2 text-sm font-mono break-all">{{ authStore.user?.xrpl_address }}</p>
        </div>

        <div class="bg-gray-50 p-4 rounded-lg">
          <h3 class="text-sm font-medium text-gray-500">Total Transactions</h3>
          <p class="mt-2 text-3xl font-semibold text-primary">{{ walletStore.transactions.length }}</p>
        </div>
      </div>
    </div>

    <!-- Transaction History -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-6">Transaction History</h2>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Transaction Hash
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="tx in sortedTransactions" :key="tx.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  {
                    'bg-green-100 text-green-800': tx.type === 'deposit',
                    'bg-blue-100 text-blue-800': tx.type === 'purchase',
                    'bg-purple-100 text-purple-800': tx.type === 'sale'
                  }
                ]">
                  {{ formatTransactionType(tx.type) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <span :class="{
                  'text-red-600': tx.type === 'purchase',
                  'text-green-600': tx.type === 'deposit' || tx.type === 'sale'
                }">
                  {{ tx.type === 'purchase' ? '-' : '+' }}{{ tx.amount }} XRP
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  {
                    'bg-green-100 text-green-800': tx.status === 'completed',
                    'bg-yellow-100 text-yellow-800': tx.status === 'pending',
                    'bg-red-100 text-red-800': tx.status === 'failed'
                  }
                ]">
                  {{ tx.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(tx.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <a 
                  :href="getXrplExplorerUrl(tx.xrpl_transaction_hash)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-primary hover:text-secondary"
                >
                  {{ truncateHash(tx.xrpl_transaction_hash) }}
                </a>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="walletStore.transactions.length === 0" class="text-center py-8">
          <p class="text-gray-500">No transactions found</p>
        </div>
      </div>
    </div>

    <!-- Deposit Modal -->
    <div v-if="showDepositModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Deposit XRP</h3>
        <p class="text-sm text-gray-600 mb-4">
          Send XRP to your wallet address:
        </p>
        <div class="bg-gray-50 p-3 rounded-md font-mono text-sm break-all">
          {{ authStore.user?.xrpl_address }}
        </div>
        <div class="mt-6 flex justify-end space-x-4">
          <button
            @click="showDepositModal = false"
            class="btn-secondary"
          >
            Close
          </button>
          <button
            @click="copyAddress"
            class="btn-primary"
          >
            Copy Address
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useWalletStore, useAuthStore } from '../store'

const walletStore = useWalletStore()
const authStore = useAuthStore()
const showDepositModal = ref(false)

onMounted(async () => {
  try {
    await walletStore.fetchTransactions()
    await walletStore.fetchBalance()
    console.log('Wallet data loaded:', {
      transactions: walletStore.transactions,
      balance: walletStore.balance
    })
  } catch (error) {
    console.error('Error initializing wallet view:', error)
  }
})

const sortedTransactions = computed(() => {
  return [...walletStore.transactions].sort((a, b) => 
    new Date(b.created_at) - new Date(a.created_at)
  )
})

const formatTransactionType = (type) => {
  switch (type) {
    case 'deposit':
      return 'Deposit'
    case 'purchase':
      return 'Purchase'
    case 'sale':
      return 'Sale'
    default:
      return type
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const truncateHash = (hash) => {
  if (!hash) return ''
  return `${hash.slice(0, 6)}...${hash.slice(-4)}`
}

const getXrplExplorerUrl = (hash) => {
  return `https://testnet.xrpl.org/transactions/${hash}`
}

const copyAddress = async () => {
  if (authStore.user?.xrpl_address) {
    await navigator.clipboard.writeText(authStore.user.xrpl_address)
  }
}
</script>
