<template>
  <div class="login-wrapper">
    <div class="login-box">
      <h2 class="title">Iniciar sesión</h2>
      <form @submit.prevent="onLogin">
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
          <label for="password">Contraseña</label>
          <div class="password-input">
            <input
              :type="showPassword ? 'text' : 'password'"
              id="password"
              v-model="password"
              placeholder="Contraseña"
              required
            />
            <button type="button" class="toggle-btn" @click="showPassword = !showPassword">
              {{ showPassword ? 'Ocultar' : 'Ver' }}
            </button>
          </div>
        </div>

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
export default {
  name: 'LoginView',
  data() {
    return {
      email: '',
      password: '',
      showPassword: false
    }
  },
  methods: {
    onLogin() {
      // Lógica de login...
      console.log('Email:', this.email, 'Password:', this.password);
    }
  }
}
</script>

<style scoped>
/* Fondo general más claro */
.login-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #ecf0f1; /* color de fondo más claro */
  padding: 1rem;
}

/* Caja de login centrada */
.login-box {
  background-color: #2c3e50; /* color del recuadro */
  padding: 2rem;
  border-radius: 8px;
  width: 320px;
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

.register-link {
  color: #e67e22;
  text-decoration: none;
  margin-left: 0.25rem;
}

.register-link:hover {
  text-decoration: underline;
}
</style>
