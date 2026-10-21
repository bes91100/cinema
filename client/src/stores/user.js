import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import Cookies from 'js-cookie'

export const useUserStore = defineStore('user', () => {
  const user = ref({})
  const loaded = ref(false)

  async function fetchUser() {
    const r = await axios.get('/api/user/info/')
    user.value = r.data
    loaded.value = true
  }

  async function login(username, password) {
    const r = await axios.post('/api/user/login/', { username, password })
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken')
    await fetchUser()
    return r.data.is_authenticated
  }

  async function logout() {
    await axios.post('/api/user/logout/')
    await fetchUser()
  }

  return { user, loaded, fetchUser, login, logout }
})
