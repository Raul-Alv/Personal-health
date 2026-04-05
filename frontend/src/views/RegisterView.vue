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
              placeholder="********"
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
              placeholder="********"
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
          Inicia sesión
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
