<template>
  <div class="page">
    <div class="ppv-content">
      <header class="ppv-header">
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
          class="ppv-item-wrapper"
        >
          <div
            class="ppv-item"
            @click="selectProcedure(proc)"
          >
            <div class="ppv-item-title">{{ proc.text }}</div>
            <div class="ppv-item-meta">
              <span class="ppv-item-code">{{ proc.code }}</span>
              <span class="ppv-item-date">{{ proc.date }}</span>
            </div>
          </div>
          <button
            class="ppv-delete-btn"
            @click.stop="deleteProcedure(proc)"
            title="Eliminar procedimiento"
          >
            🗑️
          </button>
        </div>
        <div v-if="loading" class="ppv-loading">Cargando…</div>
        <div v-if="error" class="ppv-error">Error al cargar</div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api, { clearAuthSession } from '@/api/axios'
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

function cerrarSesion() {
  clearAuthSession({ name: 'Login' })
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

async function deleteProcedure(proc) {
  if (!confirm('¿Seguro que quieres eliminar este procedimiento?')) return;
  try {
    await api.delete(
      `/mis_pacientes/${props.patient_id}/delete/procedimientos/${proc.procedure_uri.split('/').pop()}`
    );
    procedures.value = procedures.value.filter(p => p.id !== proc.id);
  } catch (e) {
    alert('Error al eliminar');
    console.error(e);
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

<style scoped src="@/styles/views/ProcedureListPage.css"></style>
