<template>
  <div class="page-container">
    <CollapsableMenu v-if="$route.meta.requiresMenu" class="menu" />
    <div class="main-content">
      <router-view/>
    </div>
  </div>
</template>

<script setup>
import CollapsableMenu from '@/views/CollapsableMenu.vue' // Asegúrate de importar el componente
</script>

<style scoped>
:root {
  --ppv-bg: #ffffff;
  --ppv-header-bg: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  --ppv-border: #e5e7eb;
  --ppv-hover-bg: #f8fafc;
  --ppv-btn-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --ppv-btn-hover: linear-gradient(135deg, #5a6fd8 0%, #6b4190 100%);
  --ppv-btn-text: #ffffff;
}

.page-container {
  display: flex; /* Usar flexbox para alinear el menú y el contenido */
  height: 100vh; /* Altura completa de la ventana */
  width: 100vw; /* Ancho completo de la ventana */
  overflow: hidden; /* Evitar overflow en el contenedor principal */
}

.menu {
  flex: 0 0 250px; /* Ancho fijo para el menú */
  /* Puedes agregar más estilos aquí para el menú */
}

.main-content {
  flex: 1; /* El contenido ocupará el resto del espacio */
  padding: 10px; /* Espaciado alrededor del contenido */
  background: var(--ppv-bg); /* Fondo del contenido */
  overflow-y: auto; /* Permitir desplazamiento vertical solo en el contenido */
}
</style>
