<template>
  <div class="register-wrapper">
    <div class="register-box">
      <h2 class="title">Registro</h2>
      <form @submit.prevent="register">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            type="email"
            v-model="email"
            placeholder="tu@correo.com"
            required
          />
        </div>

        <div class="form-group">
          <label for="name">Nombre</label>
          <input
            id="name"
            type="text"
            v-model="name"
            placeholder="Tu nombre"
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
              placeholder="••••••••"
              required
            />
            <button
              type="button"
              class="toggle-btn"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? 'Ocultar' : 'Ver' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="confirm">Repetir Contraseña</label>
          <div class="password-input">
            <input
              :type="showConfirm ? 'text' : 'password'"
              id="confirm"
              v-model="confirm"
              placeholder="••••••••"
              required
            />
            <button
              type="button"
              class="toggle-btn"
              @click="showConfirm = !showConfirm"
            >
              {{ showConfirm ? 'Ocultar' : 'Ver' }}
            </button>
          </div>
        </div>

        <button type="submit" class="submit-btn">Crear Cuenta</button>
      </form>

      <p class="bottom-text">
        ¿Ya tienes cuenta?
        <router-link to="/login" class="login-link">
          Inicia Sesión
        </router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios' // ajústalo según tu configuración

export default {
  name: 'RegisterView',
  setup() {
    const email = ref('')
    const name = ref('')
    const password = ref('')
    const confirm = ref('')
    const showPassword = ref(false)
    const showConfirm = ref(false)
    const router = useRouter()

    async function register() {
      if (password.value !== confirm.value) {
        return alert('Las contraseñas no coinciden')
      }
      try {
        await api.post('/register', {
          email: email.value,
          name: name.value,
          password: password.value
        })
        router.push('/login')
      } catch {
        alert('Error al registrar')
      }
    }

    return {
      email,
      name,
      password,
      confirm,
      showPassword,
      showConfirm,
      register
    }
  }
}
</script>

<style scoped>
/* Fondo general más claro */
.register-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #ecf0f1;
  padding: 1rem;
}

/* Caja de registro centrada */
.register-box {
  background-color: #2c3e50;
  padding: 2rem;
  border-radius: 8px;
  width: 360px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  color: #ecf0f1;
}

.title {
  margin-bottom: 1.5rem;
  text-align: center;
  font-size: 1.5rem;
  color: #fff;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #ecf0f1;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
}

/* Contenedor del campo de contraseña + botón */
.password-input {
  display: flex;
}

.password-input input {
  flex: 1;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.toggle-btn {
  padding: 0 0.75rem;
  border: none;
  background-color: #34495e;
  color: #ecf0f1;
  cursor: pointer;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  font-size: 0.9rem;
}

.toggle-btn:hover {
  background-color: #3c5a72;
}

/* Botón de envío */
.submit-btn {
  width: 100%;
  padding: 0.75rem;
  margin-top: 0.5rem;
  border: none;
  border-radius: 4px;
  background-color: #e67e22;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
}

.submit-btn:hover {
  background-color: #d35400;
}

/* Texto inferior y enlace de login */
.bottom-text {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
  color: #ecf0f1;
}

.login-link {
  color: #e67e22;
  text-decoration: none;
  margin-left: 0.25rem;
}

.login-link:hover {
  text-decoration: underline;
}
</style>
