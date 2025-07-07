<template>
  <div class="container">
    <section class="details">
      <header class="header">
        <div class="avatar">👤</div>
        <h1 class="name">
          {{ patient.nombre }} {{ patient.apellido }}
        </h1>
      </header>
        <div class="field">
            <label>Teléfono:</label>
            <span>{{ patient.telefono || 'No disponible' }}</span>
        </div>
      <div class="field">
        <label>Género:</label>
        <span>{{ patient.genero }}</span>
      </div>
      <div class="field">
        <label>Fecha de nacimiento:</label>
        <span>{{ patient.fecha_nacimiento }}</span>
      </div>
      <div class="field">
        <label>Estado civil:</label>
        <span>{{ patient.estado_civil }}</span>
      </div>
      <div class="field ssn">
        <label>Seguridad Social:</label>
        <span>{{ showSSN ? patient.ssn : maskedSSN }}</span>
        <button class="eye" @click="showSSN = !showSSN">
          {{ showSSN ? '🙈' : '👁️' }}
        </button>
      </div>

      <fieldset class="address">
        <legend>Dirección</legend>
        <div class="subfield">
          <label>Calle:</label>
          <span>{{ patient.address.calle }}</span>
        </div>
        <div class="subfield">
          <label>CP:</label>
          <span>{{ patient.address.cp }}</span>
        </div>
        <div class="subfield">
          <label>Ciudad:</label>
          <span>{{ patient.address.ciudad }}</span>
        </div>
        <div class="subfield">
          <label>Provincia:</label>
          <span>{{ patient.address.provincia }}</span>
        </div>
        <div class="subfield">
          <label>País:</label>
          <span>{{ patient.address.pais }}</span>
        </div>
      </fieldset>
    </section>

    <aside class="actions">
      <button @click="goProcedures">Ver procedimientos</button>
      <button @click="goAllergies">Ver alergias</button>
      <button @click="doExport">Exportar</button>
    </aside>

    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

// Props
const props = defineProps({
  patient_id: { type: String, required: true }
})

// Router
const router = useRouter()

// Estado reactivo
const patient = reactive({
  nombre: '',
  apellido: '',
  genero: '',
  fecha_nacimiento: '',
  estado_civil: '',
  telefono: '',
  ssn: '',
  address: {
    calle: '',
    cp: '',
    ciudad: '',
    provincia: '',
    pais: ''
  }
})
const showSSN = ref(false)
const error = ref('')

// Computed para la máscara
const maskedSSN = computed(() =>
  patient.ssn.replace(/.(?=.{4})/g, '*')
)

// Fetch de datos
async function fetchPatientDatos() {
  try {
    console.log('➡️ fetchPatientDatos() llamado')
    console.log('URL a la que llamaría:', api.getUri({ url: `/mis_pacientes/${props.patient_id}/get/datos` }))
    const { data: rows } = await api.get(
      `/mis_pacientes/${props.patient_id}/get/datos`
    )
    if (!rows.length) {
      error.value = 'No se encontraron datos del paciente'
      return
    }
    const row = rows[0]
    patient.nombre           = row.nombre || ''
    patient.apellido         = row.apellidos || ''
    patient.genero           = row.genero || ''
    patient.fecha_nacimiento = row.fechaNacimiento || ''
    patient.estado_civil     = row.estado_civil || ''
    patient.telefono         = row.telefono || ''
    patient.ssn              = row.ss || ''
    patient.address.calle    = row.calle || ''
    patient.address.cp       = row.cp || ''
    patient.address.ciudad   = row.ciudad || ''
    patient.address.provincia= row.provincia || ''
    patient.address.pais     = row.pais || ''
  } catch (e) {
    error.value =
      e.response?.data?.detail ||
      'Error al cargar datos (revisa token o permisos)'
    console.error(e)
  }
}

// Navegación y export
function goProcedures() {
  router.push({ name: 'Procedimientos', params: { id: props.patientId } })
}
function goAllergies() {
  router.push({ name: 'Alergias', params: { id: props.patientId } })
}
function doExport() {
  window.open(
    `${api.defaults.baseURL}/export_all/${props.patientId}`,
    '_blank'
  )
}

// Al montar, carga datos
onMounted(fetchPatientDatos)
</script>

<style scoped>
.container {
  display: flex;
  gap: 2rem;
  padding: 1rem;
}
.details { flex: 1; }
.header {
  display: flex;
  align-items: center;
  gap: .5rem;
  margin-bottom: 1rem;
}
.avatar { font-size: 2rem; }
.name { margin: 0; }
.field {
  display: flex;
  margin-bottom: .5rem;
}
.field label { width: 6rem; font-weight: bold; }
.field span { flex: 1; }
.ssn .eye {
  background: none;
  border: none;
  cursor: pointer;
  margin-left: .5rem;
}
.address {
  border: 1px solid #ccc;
  padding: .5rem;
  margin-top: 1rem;
}
.subfield {
  display: flex;
  margin-bottom: .5rem;
}
.subfield label { width: 6rem; }
.actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.actions button {
  padding: .75rem 1.5rem;
  cursor: pointer;
}
.error {
  position: absolute;
  bottom: 1rem;
  color: red;
}
</style>
