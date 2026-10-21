<script setup>
import { ref, computed, onBeforeMount } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const tickets = ref([])
const sessions = ref([])
const users = ref([])
const stats = ref({})
const filters = ref({})
const ticketToAdd = ref({})
const ticketToEdit = ref({})

const sessionsById = computed(() => {
  const result = {}
  for (const s of sessions.value) {
    result[s.id] = s
  }
  return result
})

async function fetchTickets() {
  const r = await axios.get('/api/tickets/', { params: filters.value })
  tickets.value = r.data
  const s = await axios.get('/api/tickets/stats/')
  stats.value = s.data
}

async function onTicketAdd() {
  await axios.post('/api/tickets/', ticketToAdd.value)
  ticketToAdd.value = {}
  await fetchTickets()
}

async function onRemoveClick(ticket) {
  try {
    await axios.delete(`/api/tickets/${ticket.id}/`)
  } catch (e) {
    alert('Сначала пройдите двойную аутентификацию в профиле')
  }
  await fetchTickets()
}

function onTicketEditClick(ticket) {
  ticketToEdit.value = { ...ticket }
}

async function onUpdateTicket() {
  try {
    await axios.put(`/api/tickets/${ticketToEdit.value.id}/`, ticketToEdit.value)
  } catch (e) {
    alert('Сначала пройдите двойную аутентификацию в профиле')
  }
  await fetchTickets()
}

onBeforeMount(async () => {
  if (userStore.user.is_superuser) {
    users.value = (await axios.get('/api/user/users/')).data
  }
  sessions.value = (await axios.get('/api/sessions/')).data
  await fetchTickets()
})
</script>

<template>
  <h2>Билеты</h2>
  <p>
    Всего: {{ stats.count }},
    выручка: {{ stats.sum_price }},
    средняя цена: {{ Math.round(stats.avg_price) }}
  </p>

  <form @submit.prevent="onTicketAdd">
    <select v-model="ticketToAdd.session" required>
      <option :value="s.id" v-for="s in sessions">Сеанс {{ s.id }}, {{ s.start }}</option>
    </select>
    <input type="number" placeholder="Место" v-model="ticketToAdd.seat" required />
    <input placeholder="Покупатель" v-model="ticketToAdd.buyer" required />
    <input type="number" placeholder="Цена" v-model="ticketToAdd.price" required />
    <button>Добавить</button>
  </form>

  <table class="table">
    <tr>
      <th>ID</th>
      <th>Сеанс</th>
      <th>Место</th>
      <th>Покупатель</th>
      <th>Цена</th>
      <th v-if="userStore.user.is_superuser">Пользователь</th>
      <th></th>
    </tr>
    <tr>
      <td></td>
      <td>
        <select v-model="filters.session" @change="fetchTickets">
          <option value="">все</option>
          <option :value="s.id" v-for="s in sessions">Сеанс {{ s.id }}, {{ s.start }}</option>
        </select>
      </td>
      <td><input type="number" v-model="filters.seat" @input="fetchTickets" /></td>
      <td><input placeholder="фильтр" v-model="filters.buyer__icontains" @input="fetchTickets" /></td>
      <td><input type="number" v-model="filters.price" @input="fetchTickets" /></td>
      <td v-if="userStore.user.is_superuser">
        <select v-model="filters.user" @change="fetchTickets">
          <option value="">все</option>
          <option :value="u.id" v-for="u in users">{{ u.username }}</option>
        </select>
      </td>
      <td></td>
    </tr>
    <tr v-for="item in tickets">
      <td>{{ item.id }}</td>
      <td>Сеанс {{ item.session }}, {{ sessionsById[item.session]?.start }}</td>
      <td>{{ item.seat }}</td>
      <td>{{ item.buyer }}</td>
      <td>{{ item.price }}</td>
      <td v-if="userStore.user.is_superuser">{{ item.user }}</td>
      <td>
        <button @click="onTicketEditClick(item)" data-bs-toggle="modal" data-bs-target="#editTicketModal">Изменить</button>
        <button @click="onRemoveClick(item)">Удалить</button>
      </td>
    </tr>
  </table>

  <div class="modal fade" id="editTicketModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-body">
          <p>
            <select v-model="ticketToEdit.session">
              <option :value="s.id" v-for="s in sessions">Сеанс {{ s.id }}, {{ s.start }}</option>
            </select>
          </p>
          <p><input type="number" placeholder="Место" v-model="ticketToEdit.seat" /></p>
          <p><input placeholder="Покупатель" v-model="ticketToEdit.buyer" /></p>
          <p><input type="number" placeholder="Цена" v-model="ticketToEdit.price" /></p>
        </div>
        <div class="modal-footer">
          <button data-bs-dismiss="modal">Закрыть</button>
          <button data-bs-dismiss="modal" @click="onUpdateTicket">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>
