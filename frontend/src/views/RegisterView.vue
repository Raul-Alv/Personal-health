<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <form @submit.prevent="register" class="bg-white p-8 rounded-xl shadow-lg w-full max-w-md animate-fade-in">
      <h2 class="text-2xl font-bold text-center text-primary-600 mb-6">Registro</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium">Email</label>
          <input v-model="email" type="email" required class="mt-1 w-full border rounded-md p-2"/>
        </div>
        <div>
          <label class="block text-sm font-medium">Nombre</label>
          <input v-model="name" type="text" required class="mt-1 w-full border rounded-md p-2"/>
        </div>
        <div>
          <label class="block text-sm font-medium">Contraseña</label>
          <input v-model="password" type="password" required class="mt-1 w-full border rounded-md p-2"/>
        </div>
        <div>
          <label class="block text-sm font-medium">Repetir Contraseña</label>
          <input v-model="confirm" type="password" required class="mt-1 w-full border rounded-md p-2"/>
        </div>
        <button type="submit" class="w-full py-2 bg-primary-600 text-white rounded-lg">Crear Cuenta</button>
      </div>
      <p class="mt-4 text-center text-sm">
        ¿Ya tienes cuenta?
        <router-link to="/login" class="text-primary-600 hover:underline">Inicia Sesión</router-link>
      </p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/axios.js'      // ← también ruta relativa aquí
import { useRouter } from 'vue-router'

const email = ref('')
const name  = ref('')
const password = ref('')
const confirm  = ref('')
const router = useRouter()

async function register() {
  if (password.value !== confirm.value) {
    return alert('Las contraseñas no coinciden')
  }
  try {
    await api.post('/register', { email: email.value, name: name.value, password: password.value })
    router.push('/login')
  } catch {
    alert('Error al registrar')
  }
}
</script>
