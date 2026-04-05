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

<script setup>
import { useLoginView } from '@/scripts/views/loginView'

const { email, password, showPassword, error, login } = useLoginView()
</script>

<style scoped src="@/styles/views/LoginView.css"></style>
