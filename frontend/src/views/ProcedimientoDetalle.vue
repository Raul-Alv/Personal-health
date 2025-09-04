<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 600 600"
    class="teeth-diagram"
  >
    <!-- Ejemplo simplificado: solo 4 dientes -->
    <path
      id="tooth-11"
      class="tooth"
      :class="{ selected: selectedIso === '11' }"
      d="M…Z"
    />
    <path
      id="tooth-12"
      class="tooth"
      :class="{ selected: selectedIso === '12' }"
      d="M…Z"
    />
    <path
      id="tooth-21"
      class="tooth"
      :class="{ selected: selectedIso === '21' }"
      d="M…Z"
    />
    <path
      id="tooth-22"
      class="tooth"
      :class="{ selected: selectedIso === '22' }"
      d="M…Z"
    />
    <!-- … el resto de tus path … -->
  </svg>
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
const router = useRouter()
const selectedIso = ref(null)
const procedures = ref([])
const loading    = ref(false)
const error      = ref(false)
async function fetchTooth() {
  loading.value = true
  error.value   = false
  try {
    const resp = await api.get(
      `/procedures/${props.patient_id}`
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

onMounted(fetchTooth)
</script>

<style scoped>
.tooth {
  fill: #f5f5f5;
  stroke: #333;
  transition: fill 0.2s;
}
.tooth.selected {
  fill: red !important;
}
</style>
