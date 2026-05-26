<template>
  <div class="login-wrapper">
    <div class="login-box">
      <div class="auth-header">
        <p class="auth-eyebrow">Acceso</p>
        <h1 class="title">Iniciar sesión</h1>
        <p class="auth-copy">
          Entra en tu espacio para consultar perfiles, procedimientos y alergias con una presentación más clara.
        </p>
      </div>
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="email">Correo electrónico</label>
          <input
            id="email"
            type="email"
            v-model="email"
            @input="error = ''"
            placeholder="nombre@correo.com"
            autocomplete="email"
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
              placeholder="Introduce tu contraseña"
              autocomplete="current-password"
              required
            />
            <button type="button" class="toggle-btn" @click="showPassword = !showPassword">
              {{ showPassword ? 'Ocultar' : 'Ver' }}
            </button>
          </div>
        </div>

        <p v-if="error" class="login-error">{{ error }}</p>

        <button type="submit" class="submit-btn">Acceder</button>
      </form>

      <p class="bottom-text">
        ¿No tienes cuenta?
        <router-link to="/register" class="register-link">Crear una cuenta</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { useLoginView } from '@/scripts/views/loginView'

const { email, password, showPassword, error, login } = useLoginView()
</script>

<style scoped src="@/styles/views/LoginView.css"></style>
