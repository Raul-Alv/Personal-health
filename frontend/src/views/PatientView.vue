<template>
  <div class="page">
    <div class="container">
      <!-- COLUMNA IZQUIERDA: DETALLES -->
      <section class="details">
        <header class="header">
          <svg class="avatar" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2c-3.3 0-10 1.7-10 5v3h20v-3c0-3.3-6.7-5-10-5z"/>
          </svg>
          <h1 class="name">{{ patient.nombre }} {{ patient.apellido }}</h1>
        </header>
        <hr class="divider–horizontal" />

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
        <div class="field ssn-field">
          <label>Seguridad Social:</label>
          <span>{{ showSSN ? patient.ssn : maskedSSN }}</span>
          <button class="eye-btn" @click="showSSN = !showSSN" :aria-label="showSSN ? 'Ocultar' : 'Mostrar'">
            <svg v-if="!showSSN" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 5c-7.633 0-11 6.5-11 6.5s3.367 6.5 11 6.5 11-6.5 11-6.5S19.633 5 12 5zm0 11a4.5 4.5 0 110-9 4.5 4.5 0 010 9z"/>
              <path d="M12 9a3 3 0 100 6 3 3 0 000-6z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7zM12 17c2.761 0 5-2.239 5-5 0-.768-.18-1.494-.5-2.142L9.142 14.5A4.98 4.98 0 0012 17zm-5-5c0 .768.18 1.494.5 2.142l7.358-7.358A4.98 4.98 0 0012 7c-2.761 0-5 2.239-5 5z"/>
            </svg>
          </button>
        </div>

        <fieldset class="address">
          <legend>Dirección</legend>
          <div class="subfield">
            <label>Calle:</label><span>{{ patient.address.calle }}</span>
          </div>
          <div class="subfield">
            <label>CP:</label><span>{{ patient.address.cp }}</span>
          </div>
          <div class="subfield">
            <label>Ciudad:</label><span>{{ patient.address.ciudad }}</span>
          </div>
          <div class="subfield">
            <label>Provincia:</label><span>{{ patient.address.provincia }}</span>
          </div>
          <div class="subfield">
            <label>País:</label><span>{{ patient.address.pais }}</span>
          </div>
        </fieldset>
      </section>

      <div class="divider–vertical"></div>

      <!-- COLUMNA DERECHA: ACCIONES -->
      <aside class="actions">
        <button class="btn secondary" @click="goProcedures">Ver procedimientos</button>
        <button class="btn secondary" @click="goAllergies">Ver alergias</button>
        <button class="btn primary"   @click="doExport">Exportar</button>
      </aside>
    </div>
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
  router.push({ name: 'Procedimientos', params: { id: props.patient_id } })
}
function goAllergies() {
  router.push({ name: 'Alergias', params: { id: props.patient_id } })
}
function doExport() {
  window.open(
    `${api.defaults.baseURL}/export_all/${props.patient_id}`,
    '_blank'
  )
}

// Al montar, carga datos
onMounted(fetchPatientDatos)
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #ecf0f1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.card {
  position: relative;
  background: #2c3e50;
  border-radius: 8px;
  padding: 2rem;
  width: 500px;
  color: #ecf0f1;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.title {
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}
.field, .ssn-field {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}
.field label, .ssn-field label {
  flex: 0 0 140px;
  font-weight: 600;
}
.value {
  flex: 1;
  background: #ecf0f1;
  color: #2c3e50;
  padding: 0.5rem;
  border-radius: 4px;
}
.address {
  border: 1px solid rgba(236,240,241,0.4);
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}
.address legend {
  padding: 0 0.5rem;
  font-weight: 600;
}
.subfield {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}
.subfield label {
  flex: 0 0 100px;
  font-size: 0.9rem;
}
.edit-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border: none;
  cursor: pointer;
  border-radius: 4px;
  font-size: 0.95rem;
  font-weight: 600;
  padding: 0.6rem 1.2rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}
.btn .icon {
  width: 1em;
  height: 1em;
}
.btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  filter: brightness(1.1);
}
.primary {
  background: #e67e22;
  color: #fff;
}
.secondary {
  background: #34495e;
  color: #ecf0f1;
}
.eye-btn {
  background: transparent;
  padding: 0.3rem;
  margin-left: 0.5rem;
  color: #ecf0f1;
}
.eye-btn:hover {
  color: #e67e22;
}
</style>
