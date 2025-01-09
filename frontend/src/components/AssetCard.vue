<template>
  <div class="bg-white rounded-xl shadow-md overflow-hidden">
    <div class="relative">
      <img 
        :src="asset.image_url" 
        :alt="asset.title"
        class="h-48 w-full object-cover"
      >
      <div 
        v-if="asset.status === 'sold'" 
        class="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded-md text-sm"
      >
        Sold
      </div>
    </div>
    
    <div class="p-4">
      <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ asset.title }}</h3>
      <p class="text-sm text-gray-600 mb-3 line-clamp-2">{{ asset.description }}</p>
      
      <div class="flex justify-between items-center">
        <div class="flex items-center space-x-1">
          <span class="text-sm text-gray-500">Owner:</span>
          <span class="text-sm font-medium text-gray-900">{{ asset.owner }}</span>
        </div>
        <div v-if="listing" class="flex items-center space-x-1">
          <span class="text-sm font-medium text-primary">{{ listing.price }} XRP</span>
        </div>
      </div>
      
      <div class="mt-4 flex space-x-2">
        <router-link 
          :to="{ name: 'asset-details', params: { id: asset.id }}"
          class="flex-1 bg-primary text-white text-center py-2 px-4 rounded-md hover:bg-secondary transition-colors"
        >
          View Details
        </router-link>
        <button 
          v-if="listing && !isOwner"
          @click="$emit('purchase', { listing, asset })"
          class="flex-1 bg-accent text-white py-2 px-4 rounded-md hover:bg-secondary transition-colors"
        >
          Purchase
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../store'

const props = defineProps({
  asset: {
    type: Object,
    required: true
  },
  listing: {
    type: Object,
    default: null
  }
})

const authStore = useAuthStore()
const isOwner = computed(() => authStore.user?.id === props.asset.owner_id)

defineEmits(['purchase'])
</script>
