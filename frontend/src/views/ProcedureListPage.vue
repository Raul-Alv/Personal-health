<template>
  <div class="ppv-container">
    <header class="ppv-header">
      <button class="ppv-btn ppv-btn-back" @click="goBack">
        ← Paciente
      </button>
      <div class="ppv-actions">
        <button class="ppv-btn ppv-btn-export" @click="exportProcedures">
          Exportar
        </button>
        <button class="ppv-btn ppv-btn-load" @click="loadProcedures">
          Cargar
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/axios'
import { useRouter } from 'vue-router'

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
  emit('select', proc)
}

/** Carga automática al montarse */
onMounted(loadProcedures)
</script>

<style scoped>
:root {
  --ppv-bg: #fff;
  --ppv-header-bg: #f9fafb;
  --ppv-border: #e5e7eb;
  --ppv-hover-bg: #f3f4f6;
  --ppv-btn-bg: #e5e7eb;
  --ppv-btn-hover: #d1d5db;
  --ppv-item-hover-animation: hover-scale 150ms ease-in-out;
}

@keyframes hover-scale {
  from { transform: scale(1); }
  to   { transform: scale(1.02); }
}

.ppv-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--ppv-bg);
}

.ppv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--ppv-header-bg);
  border-bottom: 1px solid var(--ppv-border);
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
  transition: background 120ms;
}

.ppv-btn:hover {
  background: var(--ppv-btn-hover);
}

.ppv-list {
  flex: 1;
  position: relative;
  overflow-y: auto;
}

.ppv-loading,
.ppv-error {
  padding: 1rem;
  text-align: center;
  color: #6b7280;
}

.ppv-item {
  padding: 1rem;
  border-bottom: 1px solid var(--ppv-border);
  cursor: pointer;
  transition: background 120ms, transform 150ms;
}

.ppv-item:hover {
  background: var(--ppv-hover-bg);
  animation: var(--ppv-item-hover-animation);
}

.ppv-item-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.ppv-item-meta {
  font-size: 0.875rem;
  color: #6b7280;
}

.ppv-item-meta > span + span {
  margin-left: 1rem;
}
</style>
