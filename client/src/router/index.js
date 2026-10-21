import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

import LoginView from '@/views/LoginView.vue'
import ProfileView from '@/views/ProfileView.vue'
import GenresView from '@/views/GenresView.vue'
import MoviesView from '@/views/MoviesView.vue'
import HallsView from '@/views/HallsView.vue'
import SessionsView from '@/views/SessionsView.vue'
import TicketsView from '@/views/TicketsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/movies' },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/profile', component: ProfileView },
    { path: '/genres', component: GenresView },
    { path: '/movies', component: MoviesView },
    { path: '/halls', component: HallsView },
    { path: '/sessions', component: SessionsView },
    { path: '/tickets', component: TicketsView },
  ],
})

router.beforeEach(async (to) => {
  const userStore = useUserStore()
  if (!userStore.loaded) {
    await userStore.fetchUser()
  }
  if (!userStore.user.is_authenticated && to.name !== 'login') {
    return { name: 'login' }
  }
})

export default router
