<template>
  <div class="menu-sidebar">
    <div class="menu-header">
      <button class="menu-title" @click="navegarHome">
        <h2>Personal health</h2>
      </button>
    </div>
    <div class="menu-content">
      <div class="patient-list">
        <template v-if="pacientes.length > 0">
          <div v-for="paciente in pacientes" :key="paciente.id" class="patient-item">
            <button
              @click="togglePaciente(paciente.id)"
              class="patient-button"
              :class="{ active: pacienteAbierto === paciente.id }"
            >
              <span class="toggle-icon">
                {{ pacienteAbierto === paciente.id ? 'â–¼' : 'â–¶' }}
              </span>
              <span class="patient-icon">ðŸ‘¤</span>
              <span class="patient-name">{{ paciente.nombre }} {{ paciente.apellido }}</span>
            </button>
            <transition name="slideDown">
              <div
                v-if="pacienteAbierto === paciente.id"
                class="submenu"
              >
                <button @click="navegar(paciente.id, '')" class="submenu-item">
                  <span class="submenu-icon">ðŸ“„</span>
                  Perfil
                </button>
                <button @click="navegar(paciente.id, 'procedimientos')" class="submenu-item">
                  <span class="submenu-icon">ðŸ’‰</span>
                  Procedimientos
                </button>
                <button @click="navegar(paciente.id, 'alergias')" class="submenu-item">
                  <span class="submenu-icon">âš ï¸</span>
                  Alergias
                </button>
              </div>
            </transition>
          </div>
        </template>
        <template v-else>
          <div class="no-patients">No hay pacientes disponibles.</div>
        </template>
      </div>
    </div>
    <div class="menu-actions">
      <button
        @click="navegarExportar(pacienteAbierto)"
        class="menu-action-btn"
        :disabled="!pacienteAbierto"
      >
        Exportar
      </button>
      <button
        @click="navegarImportar(pacienteAbierto)"
        class="menu-action-btn"
        :disabled="!pacienteAbierto"
      >
        Importar
      </button>
      <button
        @click="cerrarSesion"
        class="menu-action-btn menu-action-btn-logout"
      >
        Cerrar sesion
      </button>
    </div>
    <div class="resize-handle"></div>
  </div>
</template>

<script setup>
import { useCollapsableMenuView } from '@/scripts/views/collapsableMenuView'

const {
  pacientes,
  pacienteAbierto,
  togglePaciente,
  navegar,
  navegarExportar,
  navegarImportar,
  navegarHome,
  cerrarSesion
} = useCollapsableMenuView()
</script>

<style scoped src="@/styles/views/CollapsableMenu.css"></style>
