<script setup>
import { ref, computed, onBeforeMount } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const sessions = ref([])
const movies = ref([])
const halls = ref([])
const users = ref([])
const stats = ref({})
const filters = ref({})
const sessionToAdd = ref({})
const sessionToEdit = ref({})

const moviesById = computed(() => {
  const result = {}
  for (const m of movies.value) {
    result[m.id] = m
  }
  return result
})

const hallsById = computed(() => {
  const result = {}
  for (const h of halls.value) {
    result[h.id] = h
  }
  return result
})

async function fetchSessions() {
  const r = await axios.get('/api/sessions/', { params: filters.value })
  sessions.value = r.data
  const s = await axios.get('/api/sessions/stats/')
  stats.value = s.data
}

async function onSessionAdd() {
  await axios.post('/api/sessions/', sessionToAdd.value)
  sessionToAdd.value = {}
  await fetchSessions()
}

async function onRemoveClick(session) {
  try {
    await axios.delete(`/api/sessions/${session.id}/`)
  } catch (e) {
    alert('Сначала пройдите двойную аутентификацию в профиле')
  }
  await fetchSessions()
}

function onSessionEditClick(session) {
  sessionToEdit.value = { ...session }
}

async function onUpdateSession() {
  try {
    await axios.put(`/api/sessions/${sessionToEdit.value.id}/`, sessionToEdit.value)
  } catch (e) {
    alert('Сначала пройдите двойную аутентификацию в профиле')
  }
  await fetchSessions()
}

onBeforeMount(async () => {
  if (userStore.user.is_superuser) {
    users.value = (await axios.get('/api/user/users/')).data
  }
  movies.value = (await axios.get('/api/movies/')).data
  halls.value = (await axios.get('/api/halls/')).data
  await fetchSessions()
})
</script>

<template>
  <h2>Сеансы</h2>
  <p>
    Всего: {{ stats.count }},
    средняя цена: {{ Math.round(stats.avg_price) }},
    мин: {{ stats.min_price }},
    макс: {{ stats.max_price }}
  </p>

  <form @submit.prevent="onSessionAdd">
    <select v-model="sessionToAdd.movie" required>
      <option :value="m.id" v-for="m in movies">{{ m.title }}</option>
    </select>
    <select v-model="sessionToAdd.hall" required>
      <option :value="h.id" v-for="h in halls">{{ h.name }}</option>
    </select>
    <input type="datetime-local" v-model="sessionToAdd.start" required />
    <input type="number" placeholder="Цена" v-model="sessionToAdd.price" required />
    <button>Добавить</button>
  </form>

  <table class="table">
    <tr>
      <th>ID</th>
      <th>Фильм</th>
      <th>Зал</th>
      <th>Начало</th>
      <th>Цена</th>
      <th v-if="userStore.user.is_superuser">Пользователь</th>
      <th></th>
    </tr>
    <tr>
      <td></td>
      <td>
        <select v-model="filters.movie" @change="fetchSessions">
          <option value="">все</option>
          <option :value="m.id" v-for="m in movies">{{ m.title }}</option>
        </select>
      </td>
      <td>
        <select v-model="filters.hall" @change="fetchSessions">
          <option value="">все</option>
          <option :value="h.id" v-for="h in halls">{{ h.name }}</option>
        </select>
      </td>
      <td><input type="date" v-model="filters.start__date" @change="fetchSessions" /></td>
      <td><input type="number" v-model="filters.price" @input="fetchSessions" /></td>
      <td v-if="userStore.user.is_superuser">
        <select v-model="filters.user" @change="fetchSessions">
          <option value="">все</option>
          <option :value="u.id" v-for="u in users">{{ u.username }}</option>
        </select>
      </td>
      <td></td>
    </tr>
    <tr v-for="item in sessions">
      <td>{{ item.id }}</td>
      <td>{{ moviesById[item.movie]?.title }}</td>
      <td>{{ hallsById[item.hall]?.name }}</td>
      <td>{{ item.start }}</td>
      <td>{{ item.price }}</td>
      <td v-if="userStore.user.is_superuser">{{ item.user }}</td>
      <td>
        <button @click="onSessionEditClick(item)" data-bs-toggle="modal" data-bs-target="#editSessionModal">Изменить</button>
        <button @click="onRemoveClick(item)">Удалить</button>
      </td>
    </tr>
  </table>

  <div class="modal fade" id="editSessionModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-body">
          <p>
            <select v-model="sessionToEdit.movie">
              <option :value="m.id" v-for="m in movies">{{ m.title }}</option>
            </select>
          </p>
          <p>
            <select v-model="sessionToEdit.hall">
              <option :value="h.id" v-for="h in halls">{{ h.name }}</option>
            </select>
          </p>
          <p><input type="datetime-local" v-model="sessionToEdit.start" /></p>
          <p><input type="number" placeholder="Цена" v-model="sessionToEdit.price" /></p>
        </div>
        <div class="modal-footer">
          <button data-bs-dismiss="modal">Закрыть</button>
          <button data-bs-dismiss="modal" @click="onUpdateSession">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>
