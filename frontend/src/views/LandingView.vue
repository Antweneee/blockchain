<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 class="text-center text-3xl font-extrabold text-gray-900">
        Welcome to CryptoPlace
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Tokenize and trade real-world assets on the XRP Ledger
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <div v-if="showLogin">
          <!-- Login Form -->
          <form @submit.prevent="handleLogin" class="space-y-6">
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                v-model="loginForm.email"
                type="email"
                required
                class="input-field"
              >
            </div>

            <div>
              <label for="password" class="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                v-model="loginForm.password"
                type="password"
                required
                class="input-field"
              >
            </div>

            <div>
              <button type="submit" class="w-full btn-primary">
                Sign in
              </button>
            </div>
          </form>

          <div class="mt-4 text-center">
            <button 
              @click="showLogin = false" 
              class="text-sm text-primary hover:text-secondary"
            >
              Need an account? Register here
            </button>
          </div>
        </div>

        <div v-else>
          <!-- Register Form -->
          <form @submit.prevent="handleRegister" class="space-y-6">
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                id="username"
                v-model="registerForm.username"
                type="text"
                required
                class="input-field"
              >
            </div>

            <div>
              <label for="register-email" class="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="register-email"
                v-model="registerForm.email"
                type="email"
                required
                class="input-field"
              >
            </div>

            <div>
              <label for="register-password" class="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="register-password"
                v-model="registerForm.password"
                type="password"
                required
                class="input-field"
              >
            </div>

            <div>
              <button type="submit" class="w-full btn-primary">
                Register
              </button>
            </div>
          </form>

          <div class="mt-4 text-center">
            <button 
              @click="showLogin = true" 
              class="text-sm text-primary hover:text-secondary"
            >
              Already have an account? Sign in here
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store'

const router = useRouter()
const authStore = useAuthStore()
const showLogin = ref(true)

const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  username: '',
  email: '',
  password: ''
})

const handleLogin = async () => {
  try {
    await authStore.login(loginForm.value)
    router.push('/dashboard')
  } catch (error) {
    console.error('Login failed:', error)
  }
}

const handleRegister = async () => {
  try {
    await authStore.register(registerForm.value)
    showLogin.value = true
  } catch (error) {
    console.error('Registration failed:', error)
  }
}
</script>
