<!-- src/views/LoginView.vue -->
<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center px-4">
    <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
      <h2 class="text-3xl font-semibold text-center text-primary-600 mb-6">
        Iniciar Sesión
      </h2>
      <form @submit.prevent="login" class="space-y-6">
        <!-- ... -->
      </form>
      <p class="mt-4 text-center text-sm text-gray-600">
        ¿No tienes cuenta?
        <router-link to="/register" class="text-primary-600 font-medium hover:underline">
          Regístrate
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/axios.js'
import { useRouter } from 'vue-router'
import { EyeIcon, EyeOffIcon } from 'lucide-vue-next'

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const router = useRouter()

function togglePassword() {
  showPassword.value = !showPassword.value
}

async function login() {
  try {
    await api.post('/login', { email: email.value, password: password.value })
    router.push('/')
  } catch {
    alert('Credenciales erróneas')
  }
}
</script>
