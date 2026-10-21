<script setup>
import { onBeforeMount } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Cookies from 'js-cookie'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken')
})

async function onLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="container">
    <p v-if="userStore.user.is_authenticated">
      <router-link to="/genres">Жанры</router-link> |
      <router-link to="/movies">Фильмы</router-link> |
      <router-link to="/halls">Залы</router-link> |
      <router-link to="/sessions">Сеансы</router-link> |
      <router-link to="/tickets">Билеты</router-link> |
      <router-link to="/profile">Профиль</router-link> |
      <a href="/admin/">Админка</a> |
      {{ userStore.user.username }}
      <button @click="onLogout">Выйти</button>
    </p>
    <p v-else>
      <a href="/admin/">Админка</a>
    </p>

    <router-view />
  </div>
</template>
