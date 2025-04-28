import {createRouter,createWebHistory,type NavigationGuardNext} from 'vue-router'
import { useUserAuthStore } from '@/stores/userAuthStore'

const checkAuth = async () => {
  const userAuthStore = useUserAuthStore()
  if (!userAuthStore.isAuthenticated) {
    try {
      await userAuthStore.UpdateToken()
      await userAuthStore.getUserData()
      await userAuthStore.getAppData()
      userAuthStore.isAuthenticated = true
    }
    catch (e){
      
    }
  }
}

const checkUser = async (to: any, from: any, next: NavigationGuardNext) => {
  const userAuthStore = useUserAuthStore()
  userAuthStore.getAppData()
  await checkAuth()

  next()
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: ()=> import('@/views/AppView.vue'),
      beforeEnter: async (to, from, next) => {
        await checkUser(to, from, next)
      },
    },
  ],
})

export default router
