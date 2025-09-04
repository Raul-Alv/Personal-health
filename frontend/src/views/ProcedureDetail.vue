<template>
  <div v-if="loading">Cargando...</div>
  <div v-else-if="error">Error al cargar los procedimientos.</div>
  <div>
    <!-- Importas tu SVG como si fuera un componente Vue -->
    <DentaduraIconoSvg
      ref="icono"
      :width="1000"
      :height="1000"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DentaduraIconoSvg from '@/assets/Human_dental_arches.svg?component'
import api from '@/api/axios'
import { useRouter } from 'vue-router'

const icono = ref(null)
const props = defineProps({
  patient_id: {
    type: [String, Number],
    required: true
  },
  procedure_id: {
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
      `/mis_pacientes/${props.patient_id}/get/procedimientos/${props.procedure_id}`
    )
    // Asume que la respuesta es un array de { id, code, text, date }
    procedures.value = resp.data
    console.log('Procedimientos:', procedures.value)
    if (procedures.value.length > 0) {  
      // Aquí puedes manejar la lógica para seleccionar un diente
      // Por ejemplo, si el primer procedimiento tiene un código ISO
      selectedIso.value = procedures.value[0].dienteCode
      console.log('Diente seleccionado:', selectedIso.value)
      const grupo = document.getElementsByClassName(`${selectedIso.value}`)
            //.forEach(p=>p.setAttribute('fill', '#FF0000'))
      console.log('Grupo de dientes:', grupo)
      if (grupo.length > 0) {
        grupo[0].setAttribute('fill', '#FF0000') // Cambia el color del diente seleccionado
        grupo[0].addEventListener('click', pintarDientes)
      } else {

        console.warn(`No se encontró el grupo de dientes para el código ISO: ${selectedIso.value}`)
      }
    }
  } catch (e) {
    console.error(e)
    error.value = true
  } finally {
    loading.value = false
  }
}

function pintarDientes() {
  console.log('click en el SVG importado')
}

onMounted(fetchTooth)


</script>
