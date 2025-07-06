<template>
  <div
    class="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-pink-100 flex items-center justify-center p-4"
  >
    <div
      class="relative z-10 max-w-md w-full bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-2xl text-center animate-slide-up"
    >
      <h1 class="text-4xl font-extrabold text-gray-800 mb-6">
        Bienvenido a App Salud
      </h1>

      <div class="space-y-6">
        <router-link
          to="/login"
          class="block w-full py-3 text-lg font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition"
        >
          Iniciar Sesión
        </router-link>

        <p class="text-sm text-gray-600">
          ¿No tienes cuenta?
          <router-link
            to="/register"
            class="text-primary-600 font-semibold hover:underline ml-1"
          >
            Regístrate
          </router-link>
        </p>
      </div>
    </div>

    <!-- Opcionales: formas circulares animadas de fondo -->
    <div
      class="absolute -top-32 -left-32 w-72 h-72 bg-primary-600 opacity-20 rounded-full animate-pulse"
      style="animation-duration: 8s;"
    ></div>
    <div
      class="absolute -bottom-32 -right-32 w-96 h-96 bg-pink-400 opacity-15 rounded-full animate-pulse"
      style="animation-duration: 10s; animation-delay: 2s;"
    ></div>
  </div>
</template>

<script setup>
// No se necesita lógica en este componente.
</script>

<style scoped>
/* Si quieres afinar la animación pulse con más delay o duración: */
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.15; }
  50%      { transform: scale(1.1); opacity: 0.3; }
}
.animate-pulse {
  animation: pulse 6s ease-in-out infinite;
}
</style>
