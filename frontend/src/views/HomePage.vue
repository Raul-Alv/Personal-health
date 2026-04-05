<template>
  <div class="home-page">
    <div class="home-card">
      <h1 class="home-title">
        Bienvenido a App Salud
      </h1>

      <div class="home-actions">
        <router-link
          to="/login"
          class="home-login-link"
        >
          Iniciar Sesión
        </router-link>

        <p class="home-copy">
          ¿No tienes cuenta?
          <router-link
            to="/register"
            class="home-register-link"
          >
            Regístrate
          </router-link>
        </p>
      </div>
    </div>

    <div class="home-orb home-orb-primary"></div>
    <div class="home-orb home-orb-secondary"></div>
  </div>
</template>

<style scoped src="@/styles/views/HomePage.css"></style>
