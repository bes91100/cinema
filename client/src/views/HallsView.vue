<script setup>
import { ref, onBeforeMount } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const halls = ref([])
const users = ref([])
const stats = ref({})
const filters = ref({})
const hallToAdd = ref({})
const hallToEdit = ref({})

const hallsPictureRef = ref()
const hallAddImageUrl = ref()
const hallsEditPictureRef = ref()
const hallEditImageUrl = ref()
const imageToShow = ref()

async function fetchHalls() {
  const r = await axios.get('/api/halls/', { params: filters.value })
  halls.value = r.data
  const s = await axios.get('/api/halls/stats/')
  stats.value = s.data
}

function hallsAddPictureChange() {
  hallAddImageUrl.value = URL.createObjectURL(hallsPictureRef.value.files[0])
}

function hallsEditPictureChange() {
  hallEditImageUrl.value = URL.createObjectURL(hallsEditPictureRef.value.files[0])
}

async function onHallAdd() {
  const formData = new FormData()
  formData.append('name', hallToAdd.value.name)
  formData.append('capacity', hallToAdd.value.capacity)
  if (hallsPictureRef.value.files[0]) {
    formData.append('picture', hallsPictureRef.value.files[0])
  }

  await axios.post('/api/halls/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  await fetchHalls()
}

async function onRemoveClick(hall) {
  try {
    await axios.delete(`/api/halls/${hall.id}/`)
  } catch (e) {
    alert('Сначала пройдите двойную аутентификацию в профиле')
  }
  await fetchHalls()
}

function onHallEditClick(hall) {
  hallToEdit.value = { ...hall }
  hallEditImageUrl.value = hall.picture
}

async function onUpdateHall() {
  const formData = new FormData()
  formData.append('name', hallToEdit.value.name)
  formData.append('capacity', hallToEdit.value.capacity)
  if (hallsEditPictureRef.value.files[0]) {
    formData.append('picture', hallsEditPictureRef.value.files[0])
  }

  try {
    await axios.put(`/api/halls/${hallToEdit.value.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  } catch (e) {
    alert('Сначала пройдите двойную аутентификацию в профиле')
  }
  await fetchHalls()
}

onBeforeMount(async () => {
  if (userStore.user.is_superuser) {
    users.value = (await axios.get('/api/user/users/')).data
  }
  await fetchHalls()
})
</script>

<template>
  <h2>Залы</h2>
  <p>
    Всего: {{ stats.count }},
    средняя вместимость: {{ Math.round(stats.avg_capacity) }},
    самый большой: {{ stats.max_capacity }},
    всего мест: {{ stats.sum_capacity }}
  </p>

  <form @submit.prevent="onHallAdd">
    <input placeholder="Название" v-model="hallToAdd.name" required />
    <input type="number" placeholder="Вместимость" v-model="hallToAdd.capacity" required />
    <input type="file" ref="hallsPictureRef" @change="hallsAddPictureChange" />
    <img :src="hallAddImageUrl" v-if="hallAddImageUrl" height="50" />
    <button>Добавить</button>
  </form>

  <table class="table">
    <tr>
      <th>ID</th>
      <th>Фото</th>
      <th>Название</th>
      <th>Вместимость</th>
      <th v-if="userStore.user.is_superuser">Пользователь</th>
      <th></th>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td><input placeholder="фильтр" v-model="filters.name__icontains" @input="fetchHalls" /></td>
      <td><input type="number" v-model="filters.capacity" @input="fetchHalls" /></td>
      <td v-if="userStore.user.is_superuser">
        <select v-model="filters.user" @change="fetchHalls">
          <option value="">все</option>
          <option :value="u.id" v-for="u in users">{{ u.username }}</option>
        </select>
      </td>
      <td></td>
    </tr>
    <tr v-for="item in halls">
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
      <td>{{ item.name }}</td>
      <td>{{ item.capacity }}</td>
      <td v-if="userStore.user.is_superuser">{{ item.user }}</td>
      <td>
        <button @click="onHallEditClick(item)" data-bs-toggle="modal" data-bs-target="#editHallModal">Изменить</button>
        <button @click="onRemoveClick(item)">Удалить</button>
      </td>
    </tr>
  </table>

  <div class="modal fade" id="editHallModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-body">
          <p><input placeholder="Название" v-model="hallToEdit.name" /></p>
          <p><input type="number" placeholder="Вместимость" v-model="hallToEdit.capacity" /></p>
          <p><input type="file" ref="hallsEditPictureRef" @change="hallsEditPictureChange" /></p>
          <img :src="hallEditImageUrl" v-if="hallEditImageUrl" height="100" />
        </div>
        <div class="modal-footer">
          <button data-bs-dismiss="modal">Закрыть</button>
          <button data-bs-dismiss="modal" @click="onUpdateHall">Сохранить</button>
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
</template>
