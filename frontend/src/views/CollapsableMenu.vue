<template>
  <div class="menu-sidebar">
    <div class="menu-header">
      <h2 class="menu-title">Pacientes</h2>
    </div>
    <div class="menu-content">
      <div class="patient-list">
        <template v-if="pacientes.length > 0">
          <div v-for="paciente in pacientes" :key="paciente.id" class="patient-item">
            <button
              @click="togglePaciente(paciente.id)"
              class="patient-button"
              :class="{ 'active': pacienteAbierto === patient_id }"
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
                <button @click="navegar(paciente.id, 'perfil')" class="submenu-item">
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
      <button class="menu-action-btn">Exportar</button>
      <button class="menu-action-btn">Importar</button>
    </div>
    <div class="resize-handle"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '@/api/axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const pacientes = ref([])
const pacienteAbierto = ref(null)
const token = ref(localStorage.getItem('token'))

const cargarPacientes = async () => {
  try {
    console.log("Token usado en menú:", token.value)
    // Cambia el endpoint aquí para obtener los datos completos del paciente
    const { data } = await api.get('/mis_pacientes/menu')
    pacientes.value = data
    console.log("pacientes.value", pacientes.value)
  } catch (e) {
    pacientes.value = []
    console.error("Error cargando pacientes:", e)
  }
}

const togglePaciente = (id) => {
  pacienteAbierto.value = pacienteAbierto.value === id ? null : id
}
const navegar = (id, seccion) => {
  router.push(`/patient/${id}/${seccion}`)
}

onMounted(cargarPacientes)

watch(
  () => localStorage.getItem('token'),
  (newToken, oldToken) => {
    token.value = newToken
    setApiToken(newToken)
    if (newToken) cargarPacientes()
  }
)
</script>

<style scoped>
.menu-sidebar {
  width: 300px;
  min-width: 200px;
  max-width: 500px;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  position: relative;
  resize: horizontal;
  overflow: hidden;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.menu-header {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.menu-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0;
  text-align: center;
}

.menu-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.menu-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  margin-top: auto;
  background: rgba(255,255,255,0.05);
}
.menu-action-btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(102,126,234,0.15);
  transition: background 0.2s, transform 0.2s;
}
.menu-action-btn:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6b4190 100%);
  transform: translateY(-2px);
}
.no-patients {
  color: #fff;
  text-align: center;
  padding: 2rem 0;
  font-size: 1.1rem;
  opacity: 0.8;
}

.patient-list {
  padding: 0.5rem;
}

.patient-item {
  margin-bottom: 0.5rem;
}

.patient-button {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  backdrop-filter: blur(5px);
  color: #2d3748;
}

.patient-button:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.patient-button.active {
  background: rgba(102, 126, 234, 0.9);
  border-color: #667eea;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.toggle-icon {
  margin-right: 0.5rem;
  font-size: 0.875rem;
  transition: transform 0.2s ease;
  color: #64748b;
}

.patient-icon {
  margin-right: 0.5rem;
  font-size: 1rem;
}

.patient-name {
  font-weight: 500;
  flex: 1;
}

.submenu {
  margin-top: 0.5rem;
  margin-left: 1rem;
  padding-left: 1rem;
  border-left: 2px solid #e2e8f0;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.submenu-item {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.25rem;
}

.submenu-item:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.submenu-icon {
  margin-right: 0.5rem;
  font-size: 0.875rem;
}

.resize-handle {
  position: absolute;
  top: 0;
  right: 0;
  width: 4px;
  height: 100%;
  background: transparent;
  cursor: ew-resize;
  z-index: 10;
}

.resize-handle:hover {
  background: rgba(102, 126, 234, 0.8);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

/* Responsive */
@media (max-width: 768px) {
  .menu-sidebar {
    width: 100%;
    max-width: 100%;
    resize: none;
  }
}
</style>