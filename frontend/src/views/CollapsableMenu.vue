<template>
  <div class="menu-sidebar">
    <div class="menu-header">
      <button class="menu-title" type="button" @click="navegarHome">
        <span class="menu-brand-mark">
          <HeartPulse :size="18" />
        </span>
        <span class="menu-brand-copy">
          <span class="menu-brand-eyebrow">Panel clínico</span>
          <h2>Personal Health</h2>
        </span>
      </button>
    </div>
    <div class="menu-content">
      <p class="menu-section-label">Pacientes asociados</p>
      <div class="patient-list">
        <template v-if="pacientes.length > 0">
          <div v-for="paciente in pacientes" :key="paciente.id" class="patient-item">
            <button
              @click="togglePaciente(paciente.id)"
              class="patient-button"
              :class="{ active: pacienteAbierto === paciente.id }"
              type="button"
            >
              <span class="toggle-icon">
                <ChevronDown v-if="pacienteAbierto === paciente.id" :size="16" />
                <ChevronRight v-else :size="16" />
              </span>
              <span class="patient-icon">
                <UserRound :size="18" />
              </span>
              <span class="patient-name">{{ paciente.nombre }} {{ paciente.apellido }}</span>
            </button>
            <transition name="slideDown">
              <div
                v-if="pacienteAbierto === paciente.id"
                class="submenu"
              >
                <button @click="navegar(paciente.id, '')" class="submenu-item" type="button">
                  <span class="submenu-icon">
                    <FileText :size="16" />
                  </span>
                  Perfil
                </button>
                <button @click="navegar(paciente.id, 'procedimientos')" class="submenu-item" type="button">
                  <span class="submenu-icon">
                    <ClipboardList :size="16" />
                  </span>
                  Procedimientos
                </button>
                <button @click="navegar(paciente.id, 'alergias')" class="submenu-item" type="button">
                  <span class="submenu-icon">
                    <ShieldAlert :size="16" />
                  </span>
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
        type="button"
      >
        <Download :size="16" />
        Exportar
      </button>
      <button
        @click="navegarImportar(pacienteAbierto)"
        class="menu-action-btn"
        :disabled="!pacienteAbierto"
        type="button"
      >
        <Upload :size="16" />
        Importar
      </button>
      <button
        @click="cerrarSesion"
        class="menu-action-btn menu-action-btn-logout"
        type="button"
      >
        <LogOut :size="16" />
        Cerrar sesión
      </button>
    </div>
    <div class="resize-handle"></div>
  </div>
</template>

<script setup>
import {
  ChevronDown,
  ChevronRight,
  ClipboardList,
  Download,
  FileText,
  HeartPulse,
  LogOut,
  ShieldAlert,
  Upload,
  UserRound
} from 'lucide-vue-next'
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
