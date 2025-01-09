import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import axios from 'axios'
import { useAuthStore } from './store'

axios.defaults.baseURL = import.meta.env.VITE_API_URL
axios.defaults.withCredentials = true

axios.interceptors.request.use(request => {
  console.log('Starting Request', {
    url: request.url,
    method: request.method,
    data: request.data
  })
  return request
})

axios.interceptors.response.use(
  response => {
    console.log('Response:', response)
    return response
  },
  error => {
    console.error('Response Error:', error)
    const authStore = useAuthStore()
    if (error.response?.status === 401) {
      authStore.user = null
      localStorage.removeItem('user')
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

const authStore = useAuthStore(pinia)
authStore.init()

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = authStore.isAuthenticated

  if (requiresAuth && !isAuthenticated) {
    next('/landing')
  } else if (to.path === '/landing' && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

app.mount('#app')
