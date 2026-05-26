<template>
  <div class="register-wrapper">
    <div class="register-box">
      <div class="auth-header">
        <p class="auth-eyebrow">Alta de usuario</p>
        <h1 class="title">Crear cuenta</h1>
        <p class="auth-copy">
          Registra tu acceso para gestionar tu información de salud en un entorno más claro y consistente.
        </p>
      </div>
      <form @submit.prevent="register">
        <div class="form-group">
          <label for="email">Correo electrónico</label>
          <input
            id="email"
            type="email"
            v-model="email"
            placeholder="nombre@correo.com"
            autocomplete="email"
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
              placeholder="********"
              autocomplete="new-password"
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
          <label for="confirm">Confirmar contraseña</label>
          <div class="password-input">
            <input
              :type="showConfirm ? 'text' : 'password'"
              id="confirm"
              v-model="confirm"
              placeholder="********"
              autocomplete="new-password"
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

        <button type="submit" class="submit-btn">Crear cuenta</button>
      </form>

      <p class="bottom-text">
        ¿Ya tienes cuenta?
        <router-link to="/login" class="login-link">
          Iniciar sesión
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { useRegisterView } from '@/scripts/views/registerView'

const { email, name, password, confirm, showPassword, showConfirm, register } =
  useRegisterView()
</script>

<style scoped src="@/styles/views/RegisterView.css"></style>
