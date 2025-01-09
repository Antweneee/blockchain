<template>
  <div class="min-h-screen bg-gray-50">
    <nav v-if="isAuthenticated" class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <router-link 
              to="/dashboard" 
              class="flex-shrink-0 flex items-center"
            >
              <img 
                class="h-8 w-auto" 
                src="@/assets/logo.png" 
                alt="CryptoPlace" 
              />
            </router-link>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <router-link 
                v-for="item in navigationItems"
                :key="item.path"
                :to="item.path"
                class="inline-flex items-center px-1 pt-1 border-b-2"
                :class="[
                  $route.path === item.path
                    ? 'border-primary text-gray-900'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                ]"
              >
                {{ item.name }}
              </router-link>
            </div>
          </div>
          <div class="flex items-center">
            <button
              @click="logout"
              class="ml-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-secondary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './store'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => !!authStore.user)

const navigationItems = [
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Marketplace', path: '/marketplace' },
  { name: 'Wallet', path: '/wallet' },
  { name: 'Profile', path: '/profile' }
]

const logout = async () => {
  await authStore.logout()
  router.push('/landing')
}
</script>
