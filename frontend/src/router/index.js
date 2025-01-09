import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'
import DashboardView from '../views/DashboardView.vue'
import MarketplaceView from '../views/MarketplaceView.vue'
import AssetDetailsView from '../views/AssetDetailsView.vue'
import TokenizeView from '../views/TokenizeView.vue'
import WalletView from '../views/WalletView.vue'
import ProfileView from '../views/ProfileView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/landing',
      name: 'landing',
      component: LandingView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/marketplace',
      name: 'marketplace',
      component: MarketplaceView,
      meta: { requiresAuth: true }
    },
    {
      path: '/asset-details/:id',
      name: 'asset-details',
      component: AssetDetailsView,
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/tokenize',
      name: 'tokenize',
      component: TokenizeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/wallet',
      name: 'wallet',
      component: WalletView,
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/landing'
    }
  ]
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('user')

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/landing')
  } else {
    next()
  }
})

export default router
