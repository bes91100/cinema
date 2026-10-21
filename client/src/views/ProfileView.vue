<script setup>
import { ref, onBeforeMount } from 'vue'
import axios from 'axios'

const qr = ref('')
const key = ref('')
const code = ref('')
const otpGood = ref(false)

async function fetchStatus() {
  const r = await axios.get('/api/user/otp-status/')
  otpGood.value = r.data.otp_good
}

async function onOtpLogin() {
  const r = await axios.post('/api/user/otp-login/', { key: code.value })
  if (!r.data.success) {
    alert('Неверный код')
  }
  code.value = ''
  await fetchStatus()
}

onBeforeMount(async () => {
  const r = await axios.get('/api/user/otp-qr/')
  qr.value = r.data.qr
  key.value = r.data.key
  await fetchStatus()
})
</script>

<template>
  <h2>Двойная аутентификация</h2>
  <p>Отсканируйте QR-код в Google Authenticator:</p>
  <img :src="qr" width="200" />
  <p>Ключ для ручного ввода: {{ key }}</p>

  <p>Статус: {{ otpGood ? 'пройдена' : 'не пройдена' }}</p>

  <form @submit.prevent="onOtpLogin">
    <input placeholder="Код из приложения" v-model="code" required />
    <button>Подтвердить</button>
  </form>
  <p>После подтверждения можно редактировать и удалять записи 5 минут.</p>
</template>
