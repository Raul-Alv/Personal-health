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
                {{ pacienteAbierto === paciente.id ? '▼' : '▶' }}
              </span>
              <span class="patient-icon">👤</span>
              <span class="patient-name">{{ paciente.nombre }} {{ paciente.apellido }}</span>
            </button>
            <transition name="slideDown">
              <div
                v-if="pacienteAbierto === paciente.id"
                class="submenu"
              >
                <button @click="navegar(paciente.id, '')" class="submenu-item">
                  <span class="submenu-icon">📄</span>
                  Perfil
                </button>
                <button @click="navegar(paciente.id, 'procedimientos')" class="submenu-item">
                  <span class="submenu-icon">💉</span>
                  Procedimientos
                </button>
                <button @click="navegar(paciente.id, 'alergias')" class="submenu-item">
                  <span class="submenu-icon">⚠️</span>
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
    </div>
    <div class="resize-handle"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import api, { setApiToken } from '@/api/axios'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const pacientes = ref([])
const pacienteAbierto = ref(null)
const token = ref(localStorage.getItem('token'))

const currentPatientId = computed(() => {
  return route.params.patient_id || route.params.id || route.params.patientId || null
})

const cargarPacientes = async () => {
  try {
    const { data } = await api.get('/mis_pacientes/menu')
    pacientes.value = data

    if (currentPatientId.value) {
      pacienteAbierto.value = currentPatientId.value
    }
  } catch (e) {
    pacientes.value = []
    console.error('Error cargando pacientes:', e)
  }
}

const togglePaciente = async (id) => {
  const yaEstabaAbierto = pacienteAbierto.value === id
  pacienteAbierto.value = yaEstabaAbierto ? null : id

  if (!yaEstabaAbierto) {
    await router.push(`/patient/${id}`)
  }
}

const navegar = (id, seccion) => {
  if (!seccion) {
    router.push(`/patient/${id}`)
    return
  }
  router.push(`/patient/${id}/${seccion}`)
}

const navegarExportar = (patientId) => {
  if (patientId) {
    router.push('/export/')
  } else {
    alert('Por favor, selecciona un paciente primero')
  }
}

const navegarImportar = (patientId) => {
  if (patientId) {
    router.push('/import/')
  } else {
    alert('Por favor, selecciona un paciente primero')
  }
}

const navegarHome = () => {
  router.push('/profile')
}

onMounted(cargarPacientes)

watch(
  () => currentPatientId.value,
  (newPatientId) => {
    if (newPatientId) {
      pacienteAbierto.value = newPatientId
    }
  },
  { immediate: true }
)

watch(
  () => route.fullPath,
  () => {
    if (currentPatientId.value) {
      pacienteAbierto.value = currentPatientId.value
    }
  }
)

watch(
  () => localStorage.getItem('token'),
  (newToken) => {
    token.value = newToken
    setApiToken(newToken)
    if (newToken) cargarPacientes()
  }
)
</script>

<style scoped src="@/styles/views/CollapsableMenu.css"></style>
