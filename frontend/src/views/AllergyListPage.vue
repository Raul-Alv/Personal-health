<template>
  <div class="ppv-container">
    <header class="ppv-header">
        <div class="ppv-actions">
          <button class="ppv-btn ppv-btn-export" @click="cerrarSesion">
            Cerrar sesión
          </button>
        </div> 
      </header>

    <div class="ppv-list">
      <div
        v-for="al in allergies"
        :key="al.id"
        class="ppv-item"
        @click="selectAllergy(al)"
      >
        <div class="ppv-item-title">{{ al.display }}</div>
        <div class="ppv-item-meta">
          <span class="ppv-item-code">{{ al.code }}</span>
          <span class="ppv-item-date">{{ al.onsetDateTime }}</span>
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

/** ID del paciente para las llamadas */
const props = defineProps({
  patient_id: {
    type: [String, Number],
    required: true
  }
})
const emit = defineEmits(['back', 'select'])

/** Estado interno */
const allergies = ref([])
const loading    = ref(false)
const error      = ref(false)

/** Carga la lista desde el backend */
async function loadAllergies() {
  loading.value = true
  error.value   = false
  try {
    const resp = await api.get(
      `/mis_pacientes/${props.patient_id}/get/alergias`
    )
    // Asume que la respuesta es un array de { id, code, text, date }
    allergies.value = resp.data
  } catch (e) {
    console.error(e)
    error.value = true
  } finally {
    loading.value = false
  }
}

/** Lanza la exportación (descarga CSV, JSON, lo que sea) */
async function exportAllergies() {
  try {
    const resp = await api.get(
      `/api/mis_pacientes/${props.patient_id}/alergias/export`,
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
function selectAllergy(proc) {
  emit('select', proc)
}

/** Carga automática al montarse */
onMounted(loadAllergies)
</script>

<style scoped src="@/styles/views/AllergyListPage.css"></style>
