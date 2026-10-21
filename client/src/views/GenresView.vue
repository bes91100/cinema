<script setup>
import { ref, onBeforeMount } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const genres = ref([])
const users = ref([])
const stats = ref({})
const filters = ref({})
const genreToAdd = ref({})
const genreToEdit = ref({})

async function fetchGenres() {
  const r = await axios.get('/api/genres/', { params: filters.value })
  genres.value = r.data
  const s = await axios.get('/api/genres/stats/')
  stats.value = s.data
}

async function onGenreAdd() {
  await axios.post('/api/genres/', genreToAdd.value)
  genreToAdd.value = {}
  await fetchGenres()
}

async function onRemoveClick(genre) {
  try {
    await axios.delete(`/api/genres/${genre.id}/`)
  } catch (e) {
    alert('Сначала пройдите двойную аутентификацию в профиле')
  }
  await fetchGenres()
}

function onGenreEditClick(genre) {
  genreToEdit.value = { ...genre }
}

async function onUpdateGenre() {
  try {
    await axios.put(`/api/genres/${genreToEdit.value.id}/`, genreToEdit.value)
  } catch (e) {
    alert('Сначала пройдите двойную аутентификацию в профиле')
  }
  await fetchGenres()
}

onBeforeMount(async () => {
  if (userStore.user.is_superuser) {
    users.value = (await axios.get('/api/user/users/')).data
  }
  await fetchGenres()
})
</script>

<template>
  <h2>Жанры</h2>
  <p>Всего жанров: {{ stats.count }}</p>

  <form @submit.prevent="onGenreAdd">
    <input placeholder="Название" v-model="genreToAdd.name" required />
    <button>Добавить</button>
  </form>

  <table class="table">
    <tr>
      <th>ID</th>
      <th>Название</th>
      <th v-if="userStore.user.is_superuser">Пользователь</th>
      <th></th>
    </tr>
    <tr>
      <td></td>
      <td><input placeholder="фильтр" v-model="filters.name__icontains" @input="fetchGenres" /></td>
      <td v-if="userStore.user.is_superuser">
        <select v-model="filters.user" @change="fetchGenres">
          <option value="">все</option>
          <option :value="u.id" v-for="u in users">{{ u.username }}</option>
        </select>
      </td>
      <td></td>
    </tr>
    <tr v-for="item in genres">
      <td>{{ item.id }}</td>
      <td>{{ item.name }}</td>
      <td v-if="userStore.user.is_superuser">{{ item.user }}</td>
      <td>
        <button @click="onGenreEditClick(item)" data-bs-toggle="modal" data-bs-target="#editGenreModal">Изменить</button>
        <button @click="onRemoveClick(item)">Удалить</button>
      </td>
    </tr>
  </table>

  <div class="modal fade" id="editGenreModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-body">
          <input placeholder="Название" v-model="genreToEdit.name" />
        </div>
        <div class="modal-footer">
          <button data-bs-dismiss="modal">Закрыть</button>
          <button data-bs-dismiss="modal" @click="onUpdateGenre">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>
