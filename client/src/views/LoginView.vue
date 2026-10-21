<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref(false)

async function onLogin() {
  if (await userStore.login(username.value, password.value)) {
    router.push('/movies')
  } else {
    error.value = true
  }
}
</script>

<template>
  <h2>Вход</h2>
  <form @submit.prevent="onLogin">
    <p><input placeholder="Логин" v-model="username" required /></p>
    <p><input type="password" placeholder="Пароль" v-model="password" required /></p>
    <p v-if="error">Неверный логин или пароль</p>
    <button>Войти</button>
  </form>
</template>
