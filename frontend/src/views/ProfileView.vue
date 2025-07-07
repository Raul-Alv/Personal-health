<template>
  <div>
    <header class="flex justify-between items-center p-4 bg-gray-100">
      <div>
        <h1 class="text-xl font-bold">{{ user.nombre }}</h1>
        <p class="text-sm text-gray-600">{{ user.email }}</p>
      </div>
      <button @click="logout" class="text-red-500">Cerrar sesión</button>
    </header>
    <main class="p-4">
      <h2 class="text-lg mb-4">Mis Pacientes</h2>
      <div class="grid grid-cols-3 gap-4">
        <div
          v-for="pac in pacientes"
          :key="pac.id"
          class="border p-2 rounded hover:shadow cursor-pointer"
        >
          <router-link :to="`/patient/${pac.id}`">
            <h3 class="font-semibold">{{ pac.nombre }} {{ pac.apellido }}</h3>
          </router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import api from '@/api/axios'
export default {
  name: 'ProfileView',
  data() {
    return {
      user: { nombre: '', email: '' },
      pacientes: []
    }
  },
  async created() {
    try {
      const resU = await api.get('/me/')
      this.user = resU.data
      const resP = await api.get('/mis_pacientes/')
      this.pacientes = resP.data
    } catch {
      this.$router.push('/login')
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
      this.$router.push('/')
    }
  }
}
</script>
