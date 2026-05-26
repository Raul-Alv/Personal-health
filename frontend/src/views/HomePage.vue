<template>
  <div class="home-page">
    <div class="home-card">
      <p class="home-eyebrow">Gestión de salud personal</p>
      <h1 class="home-title">
        Una interfaz más clara para tu información clínica
      </h1>
      <p class="home-copy">
        Accede a tus pacientes, procedimientos y alergias desde un espacio ordenado, sin distracciones y con un lenguaje más cuidado.
      </p>

      <div class="home-actions">
        <router-link
          to="/login"
          class="home-login-link"
        >
          Iniciar sesión
        </router-link>

        <p class="home-register-copy">
          ¿Todavía no tienes cuenta?
          <router-link
            to="/register"
            class="home-register-link"
          >
            Crear una cuenta
          </router-link>
        </p>
      </div>
    </div>

    <div class="home-orb home-orb-primary"></div>
    <div class="home-orb home-orb-secondary"></div>
  </div>
</template>

<style scoped src="@/styles/views/HomePage.css"></style>
