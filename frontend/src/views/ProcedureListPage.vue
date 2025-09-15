<template>
  <div class="page-container">
    <CollapsableMenu />
    <div class="main-content">
      <header class="ppv-header">
        <button class="ppv-btn ppv-btn-back" @click="goBack">
          ← Paciente
        </button>
        <div class="ppv-actions">
          <button class="ppv-btn ppv-btn-export" @click="cerrarSesion">
            Cerrar sesión
          </button>
        </div> 
      </header>
      
      <div class="ppv-list">
        <div
          v-for="proc in procedures"
          :key="proc.id"
          class="ppv-item"
          @click="selectProcedure(proc)"
        >
            <div class="ppv-item-title">{{ proc.text }}</div>
            <div class="ppv-item-meta">
              <span class="ppv-item-code">{{ proc.code }}</span>
              <span class="ppv-item-date">{{ proc.date }}</span>
            </div>
        </div>
        <div v-if="loading" class="ppv-loading">Cargando…</div>
        <div v-if="error" class="ppv-error">Error al cargar</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/axios'
import { useRouter } from 'vue-router'
import CollapsableMenu from './CollapsableMenu.vue'

/** ID del paciente para las llamadas */
const props = defineProps({
  patient_id: {
    type: [String, Number],
    required: true
  }
})
const emit = defineEmits(['back', 'select'])

/** Estado interno */
const procedures = ref([])
const loading    = ref(false)
const error      = ref(false)

const router = useRouter()

function goBack() {
  router.back()
}

function cerrarSesion() {
  localStorage.removeItem("token");
  router.push("/login");
}

/** Carga la lista desde el backend */
async function loadProcedures() {
  loading.value = true
  error.value   = false
  try {
    const resp = await api.get(
      `/mis_pacientes/${props.patient_id}/get/procedimientos`
    )
    // Asume que la respuesta es un array de { id, code, text, date }
    procedures.value = resp.data
  } catch (e) {
    console.error(e)
    error.value = true
  } finally {
    loading.value = false
  }
}

/** Lanza la exportación (descarga CSV, JSON, lo que sea) */
async function exportProcedures() {
  try {
    const resp = await api.get(
      `/api/mis_pacientes/${props.patient_id}/procedures/export`,
      { responseType: 'blob' }
    )
    // Crea un enlace para descargar
    const url = URL.createObjectURL(new Blob([resp.data]))
    const a = document.createElement('a')
    a.href = url
    a.setAttribute('download', `procedures_${props.patient_id}.csv`)
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error(e)
    alert('Error al exportar')
  }
}

/** Selecciona uno y emite al padre */
function selectProcedure(proc) {
  console.log(proc)
  router.push(`/patient/${props.patient_id}/procedimientos/${proc.procedure_uri.split('/').pop()}`)
}

/** Carga automática al montarse */
onMounted(loadProcedures)
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
  --ppv-item-hover-animation: hover-scale 150ms ease-in-out;
}

@keyframes hover-scale {
  from { transform: scale(1); }
  to   { transform: scale(1.02); }
}

.page-container {
  display: grid;
  grid-template-columns: auto 1fr;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
}

.main-content {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--ppv-bg);
  overflow: hidden;
}

.ppv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--ppv-header-bg);
  border-bottom: 1px solid var(--ppv-border);
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.ppv-actions > .ppv-btn {
  margin-left: 0.5rem;
}

.ppv-btn {
  padding: 0.5rem 1rem;
  background: var(--ppv-btn-bg);
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 120ms ease;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ppv-btn-text);
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.ppv-btn:hover {
  background: var(--ppv-btn-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.ppv-list {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  overflow-x: hidden;
}

.ppv-loading,
.ppv-error {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  font-style: italic;
}

.ppv-error {
  color: #dc2626;
}

.ppv-item {
  padding: 1rem;
  border: 1px solid var(--ppv-border);
  border-radius: 0.5rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: var(--ppv-item-hover-animation);
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.ppv-item:hover {
  background: var(--ppv-hover-bg);
  border-color: rgba(102, 126, 234, 0.3);
  animation: hover-scale;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-1px);
}

.ppv-item-title {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

.ppv-item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: #64748b;
}

.ppv-item-code {
  font-family: monospace;
  background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 500;
  color: #0369a1;
  border: 1px solid rgba(3, 105, 161, 0.2);
}

.ppv-item-date {
  font-weight: 500;
  color: #475569;
}

/* Responsive */
@media (max-width: 768px) {
  .page-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
  
  .ppv-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .ppv-actions {
    display: flex;
    justify-content: space-between;
  }
  
  .ppv-actions > .ppv-btn {
    margin-left: 0;
    flex: 1;
    margin-right: 0.25rem;
  }
  
  .ppv-actions > .ppv-btn:last-child {
    margin-right: 0;
  }
}
</style>
