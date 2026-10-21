<script setup>
import { ref, computed, onBeforeMount } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const movies = ref([])
const genres = ref([])
const users = ref([])
const stats = ref({})
const filters = ref({})
const movieToAdd = ref({})
const movieToEdit = ref({})

const moviesPictureRef = ref()
const movieAddImageUrl = ref()
const moviesEditPictureRef = ref()
const movieEditImageUrl = ref()
const imageToShow = ref()

const albumMovie = ref({})
const photos = ref([])
const photoRef = ref()

const genresById = computed(() => {
  const result = {}
  for (const g of genres.value) {
    result[g.id] = g
  }
  return result
})

async function fetchMovies() {
  const r = await axios.get('/api/movies/', { params: filters.value })
  movies.value = r.data
  const s = await axios.get('/api/movies/stats/')
  stats.value = s.data
}

function moviesAddPictureChange() {
  movieAddImageUrl.value = URL.createObjectURL(moviesPictureRef.value.files[0])
}

function moviesEditPictureChange() {
  movieEditImageUrl.value = URL.createObjectURL(moviesEditPictureRef.value.files[0])
}

async function onMovieAdd() {
  const formData = new FormData()
  formData.append('title', movieToAdd.value.title)
  formData.append('year', movieToAdd.value.year)
  formData.append('duration', movieToAdd.value.duration)
  formData.append('genre', movieToAdd.value.genre)
  if (moviesPictureRef.value.files[0]) {
    formData.append('picture', moviesPictureRef.value.files[0])
  }

  await axios.post('/api/movies/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  await fetchMovies()
}

async function onRemoveClick(movie) {
  try {
    await axios.delete(`/api/movies/${movie.id}/`)
  } catch (e) {
    alert('Сначала пройдите двойную аутентификацию в профиле')
  }
  await fetchMovies()
}

function onMovieEditClick(movie) {
  movieToEdit.value = { ...movie }
  movieEditImageUrl.value = movie.picture
}

async function onUpdateMovie() {
  const formData = new FormData()
  formData.append('title', movieToEdit.value.title)
  formData.append('year', movieToEdit.value.year)
  formData.append('duration', movieToEdit.value.duration)
  formData.append('genre', movieToEdit.value.genre)
  if (moviesEditPictureRef.value.files[0]) {
    formData.append('picture', moviesEditPictureRef.value.files[0])
  }

  try {
    await axios.put(`/api/movies/${movieToEdit.value.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  } catch (e) {
    alert('Сначала пройдите двойную аутентификацию в профиле')
  }
  await fetchMovies()
}

async function fetchPhotos() {
  const r = await axios.get('/api/movie-photos/', { params: { movie: albumMovie.value.id } })
  photos.value = r.data
}

async function onAlbumClick(movie) {
  albumMovie.value = movie
  await fetchPhotos()
}

async function onPhotoAdd() {
  const formData = new FormData()
  formData.append('movie', albumMovie.value.id)
  formData.append('picture', photoRef.value.files[0])

  await axios.post('/api/movie-photos/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  await fetchPhotos()
}

async function onPhotoRemove(photo) {
  try {
    await axios.delete(`/api/movie-photos/${photo.id}/`)
  } catch (e) {
    alert('Сначала пройдите двойную аутентификацию в профиле')
  }
  await fetchPhotos()
}

onBeforeMount(async () => {
  if (userStore.user.is_superuser) {
    users.value = (await axios.get('/api/user/users/')).data
  }
  genres.value = (await axios.get('/api/genres/')).data
  await fetchMovies()
})
</script>

<template>
  <h2>Фильмы</h2>
  <p>
    Всего: {{ stats.count }},
    годы: {{ stats.min_year }}–{{ stats.max_year }},
    средний год: {{ Math.round(stats.avg_year) }},
    средняя длительность: {{ Math.round(stats.avg_duration) }} мин
  </p>
  <p><a href="/api/movies/export/">Скачать в Excel</a></p>

  <form @submit.prevent="onMovieAdd">
    <input placeholder="Название" v-model="movieToAdd.title" required />
    <input type="number" placeholder="Год" v-model="movieToAdd.year" required />
    <input type="number" placeholder="Длительность" v-model="movieToAdd.duration" required />
    <select v-model="movieToAdd.genre" required>
      <option :value="g.id" v-for="g in genres">{{ g.name }}</option>
    </select>
    <input type="file" ref="moviesPictureRef" @change="moviesAddPictureChange" />
    <img :src="movieAddImageUrl" v-if="movieAddImageUrl" height="50" />
    <button>Добавить</button>
  </form>

  <table class="table">
    <tr>
      <th>ID</th>
      <th>Постер</th>
      <th>Название</th>
      <th>Год</th>
      <th>Длительность</th>
      <th>Жанр</th>
      <th v-if="userStore.user.is_superuser">Пользователь</th>
      <th></th>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td><input placeholder="фильтр" v-model="filters.title__icontains" @input="fetchMovies" /></td>
      <td><input type="number" v-model="filters.year" @input="fetchMovies" /></td>
      <td><input type="number" v-model="filters.duration" @input="fetchMovies" /></td>
      <td>
        <select v-model="filters.genre" @change="fetchMovies">
          <option value="">все</option>
          <option :value="g.id" v-for="g in genres">{{ g.name }}</option>
        </select>
      </td>
      <td v-if="userStore.user.is_superuser">
        <select v-model="filters.user" @change="fetchMovies">
          <option value="">все</option>
          <option :value="u.id" v-for="u in users">{{ u.username }}</option>
        </select>
      </td>
      <td></td>
    </tr>
    <tr v-for="item in movies">
      <td>{{ item.id }}</td>
      <td>
        <img
          v-if="item.picture"
          :src="item.picture"
          height="50"
          @click="imageToShow = item.picture"
          data-bs-toggle="modal"
          data-bs-target="#imageModal"
        />
      </td>
      <td>{{ item.title }}</td>
      <td>{{ item.year }}</td>
      <td>{{ item.duration }}</td>
      <td>{{ genresById[item.genre]?.name }}</td>
      <td v-if="userStore.user.is_superuser">{{ item.user }}</td>
      <td>
        <button @click="onAlbumClick(item)" data-bs-toggle="modal" data-bs-target="#albumModal">Альбом</button>
        <button @click="onMovieEditClick(item)" data-bs-toggle="modal" data-bs-target="#editMovieModal">Изменить</button>
        <button @click="onRemoveClick(item)">Удалить</button>
      </td>
    </tr>
  </table>

  <div class="modal fade" id="editMovieModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-body">
          <p><input placeholder="Название" v-model="movieToEdit.title" /></p>
          <p><input type="number" placeholder="Год" v-model="movieToEdit.year" /></p>
          <p><input type="number" placeholder="Длительность" v-model="movieToEdit.duration" /></p>
          <p>
            <select v-model="movieToEdit.genre">
              <option :value="g.id" v-for="g in genres">{{ g.name }}</option>
            </select>
          </p>
          <p><input type="file" ref="moviesEditPictureRef" @change="moviesEditPictureChange" /></p>
          <img :src="movieEditImageUrl" v-if="movieEditImageUrl" height="100" />
        </div>
        <div class="modal-footer">
          <button data-bs-dismiss="modal">Закрыть</button>
          <button data-bs-dismiss="modal" @click="onUpdateMovie">Сохранить</button>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="imageModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body">
          <img :src="imageToShow" class="img-fluid" />
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="albumModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body">
          <h4>Альбом: {{ albumMovie.title }}</h4>
          <form @submit.prevent="onPhotoAdd">
            <input type="file" ref="photoRef" required />
            <button>Добавить фото</button>
          </form>
          <div v-for="p in photos">
            <img :src="p.picture" height="150" />
            <button @click="onPhotoRemove(p)">Удалить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
