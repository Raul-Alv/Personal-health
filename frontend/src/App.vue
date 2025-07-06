<template>
  <nav>
    <router-link to="/">Home</router-link>
    <router-link to="/login">Login</router-link>
    <router-link to="/register">Register</router-link>
  </nav>

  <!-- aquí Vue montará HomePage, LoginView o RegisterView -->
  <router-view/>
</template>

<script setup>
// ya no necesitas importar HomePage aquí
</script>

<style scoped>
/* tu CSS… */
</style>
