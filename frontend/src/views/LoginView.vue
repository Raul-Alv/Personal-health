<template>
  <div class="login-wrapper">
    <div class="login-box">
      <h2 class="title">Iniciar sesión</h2>
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            type="email"
            v-model="email"
            @input="error = ''"
            placeholder="tu@correo.com"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Contraseña</label>
          <div class="password-input">
            <input
              :type="showPassword ? 'text' : 'password'"
              id="password"
              v-model="password"
              @input="error = ''"
              placeholder="Contraseña"
              required
            />
            <button type="button" class="toggle-btn" @click="showPassword = !showPassword">
              {{ showPassword ? 'Ocultar' : 'Ver' }}
            </button>
          </div>
        </div>

        <p v-if="error" class="login-error">{{ error }}</p>

        <button type="submit" class="submit-btn">Entrar</button>
      </form>

      <p class="bottom-text">
        ¿No tienes cuenta?
        <router-link to="/register" class="register-link">Regístrate</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import api, { setApiToken } from '@/api/axios'

export default {
  name: 'LoginView',
  data() {
    return {
      email: '',
      password: '',
      showPassword: false,
      error: ''
    }
  },
  mounted() {
    console.log('LoginView montado')
  },
  methods: {
    async login() {
      this.error = ''

      try {
        const params = new URLSearchParams()
        params.append('email', this.email)
        params.append('password', this.password)

        const res = await api.post('/login/', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        })

        localStorage.setItem('token', res.data.access_token)
        setApiToken(res.data.access_token)
        this.$router.push('/profile')
      } catch (e) {
        const detail = e.response?.data?.detail || ''
        const normalizedDetail = detail.toLowerCase()

        if (normalizedDetail.includes('contrase')) {
          this.password = ''
          this.showPassword = false
          this.error = 'Contraseña incorrecta'
          return
        }

        if (normalizedDetail.includes('usuario no encontrado')) {
          this.error = 'No existe ningún usuario con ese email'
          return
        }

        this.error = detail || 'Error en el login'
      }
    }
  }
}
</script>

<style scoped src="@/styles/views/LoginView.css"></style>
