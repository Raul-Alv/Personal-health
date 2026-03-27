<template>
  <div class="page">
    <div
      v-if="isEditing"
      class="overlay"
    ></div>
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
        <!-- Botones -->
        <button
          v-if="!isEditing"
          @click="startEdit"
          class="btn edit-btn"
        >
          Editar
        </button>

        <div v-else class="edit-actions">
          <button
            @click="openConfirmSave"
            class="btn save-btn"
          >
            Guardar
          </button>
          <button
            @click="cancelEdit"
            class="btn cancel-btn"
          >
            Cancelar
          </button>
        </div>
      
        <div class="field">
          <label>Género:</label>
          <span
          :contenteditable="isEditing"
          @input="onInput('genero', $event)"
          class="editable-field">{{ patient.genero }}</span>
        </div>
        <div class="field">
          <label>Fecha de nacimiento:</label>
          <span
          :contenteditable="isEditing"
          @input="onInput('fecha_nacimiento', $event)"
          class="editable-field">{{ patient.fecha_nacimiento }}</span>
        </div>
        <div class="field">
          <label>Estado civil:</label>
          <span
          :contenteditable="isEditing"
          @input="onInput('estado_civil', $event)"
          class="editable-field">{{ patient.estado_civil }}</span>
        </div>
        <div class="field ssn-field">
          <label>Seguridad Social:</label>
          <span
          :contenteditable="isEditing"
          @input="onInput('ssn', $event)"
          class="editable-field">{{ showSSN ? patient.ssn : maskedSSN }}</span>
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
            <label>Calle:</label>
            <span
            :contenteditable="isEditing"
            @input="onInput('calle', $event)"
            class="editable-field">{{ patient.address.calle }}</span>
          </div>
          <div class="subfield">
            <label>CP:</label>
            <span
            :contenteditable="isEditing"
            @input="onInput('cp', $event)"
            class="editable-field">{{ patient.address.cp }}</span>
          </div>
          <div class="subfield">
            <label>Ciudad:</label>
            <span
            :contenteditable="isEditing"
            @input="onInput('ciudad', $event)"
            class="editable-field">{{ patient.address.ciudad }}</span>
          </div>
          <div class="subfield">
            <label>Provincia:</label>
            <span
            :contenteditable="isEditing"
            @input="onInput('provincia', $event)"
            class="editable-field">{{ patient.address.provincia }}</span>
          </div>
          <div class="subfield">
            <label>País:</label>
            <span
            :contenteditable="isEditing"
            @input="onInput('pais', $event)"
            class="editable-field">{{ patient.address.pais }}</span>
          </div>
        </fieldset>
      </section>

      <div class="divider–vertical"></div>

      <!-- COLUMNA DERECHA: ACCIONES -->
      <!-- COLUMNA DERECHA: ACCIONES -->
      <aside class="actions">
        <button
          class="btn secondary"
          @click="goProcedures"
          :disabled="isEditing"
        >
          Ver procedimientos
        </button>

        <button
          class="btn secondary"
          @click="goAllergies"
          :disabled="isEditing"
        >
          Ver alergias
        </button>

        <button
          class="btn primary"
          @click="doExport"
          :disabled="isEditing"
        >
          Exportar
        </button>
      </aside>
    </div>
  </div>
  <!-- Modal confirmar guardado -->
  <div v-if="showSaveConfirm" class="modal-backdrop">
    <div class="modal-box">
      <h3>Confirmar edición</h3>
      <p>¿Quieres guardar los cambios de este perfil?</p>
      <div class="modal-actions">
        <button class="btn save-btn" @click="confirmSave">Sí, guardar</button>
        <button class="btn cancel-btn" @click="showSaveConfirm = false">No</button>
      </div>
    </div>
  </div>

  <!-- Modal guardado correcto -->
  <div v-if="showSavedMessage" class="modal-backdrop">
    <div class="modal-box">
      <h3>Cambios guardados</h3>
      <p>El perfil se ha actualizado correctamente.</p>
      <div class="modal-actions">
        <button class="btn save-btn" @click="showSavedMessage = false">Aceptar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

const props = defineProps({
  patient_id: { type: String, required: true }
})

const router = useRouter()

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
const isEditing = ref(false)
const showSaveConfirm = ref(false)
const showSavedMessage = ref(false)

const original = ref({})
const edited = reactive({
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

const maskedSSN = computed(() =>
  (patient.ssn || '').replace(/.(?=.{4})/g, '*')
)

function fillEditedFromPatient() {
  edited.nombre = patient.nombre
  edited.apellido = patient.apellido
  edited.genero = patient.genero
  edited.fecha_nacimiento = patient.fecha_nacimiento
  edited.estado_civil = patient.estado_civil
  edited.telefono = patient.telefono
  edited.ssn = patient.ssn
  edited.address = {
    calle: patient.address.calle,
    cp: patient.address.cp,
    ciudad: patient.address.ciudad,
    provincia: patient.address.provincia,
    pais: patient.address.pais
  }
}

function resetPatient() {
  patient.nombre = ''
  patient.apellido = ''
  patient.genero = ''
  patient.fecha_nacimiento = ''
  patient.estado_civil = ''
  patient.telefono = ''
  patient.ssn = ''
  patient.address.calle = ''
  patient.address.cp = ''
  patient.address.ciudad = ''
  patient.address.provincia = ''
  patient.address.pais = ''
}

function startEdit() {
  original.value = JSON.parse(JSON.stringify(patient))
  fillEditedFromPatient()
  isEditing.value = true
}

function openConfirmSave() {
  showSaveConfirm.value = true
}

function onInput(field, event) {
  const value = event.target.innerText.trim()

  const addressFields = ['calle', 'cp', 'ciudad', 'provincia', 'pais']
  if (addressFields.includes(field)) {
    edited.address[field] = value
    return
  }

  edited[field] = value
}

function escapeTurtleLiteral(value) {
  return String(value ?? '')
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\r/g, '\\r')
    .replace(/\n/g, '\\n')
}

function buildPatientPatchTurtle(data) {
  const patientUri = `http://hl7.org/fhir/Patient/${props.patient_id}`

  return `@prefix fhir: <http://hl7.org/fhir/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<${patientUri}>
  fhir:Patient.gender [
    fhir:value "${escapeTurtleLiteral(data.genero)}"
  ] ;
  fhir:Patient.birthDate [
    fhir:value "${escapeTurtleLiteral(data.fecha_nacimiento)}"
  ] ;
  fhir:Patient.maritalStatus [
    fhir:value "${escapeTurtleLiteral(data.estado_civil)}"
  ] ;
  fhir:Patient.identifier [
    fhir:Identifier.value [
      fhir:value "${escapeTurtleLiteral(data.ssn)}"
    ]
  ] ;
  fhir:Patient.telecom [
    fhir:ContactPoint.value [
      fhir:value "${escapeTurtleLiteral(data.telefono)}"
    ]
  ] ;
  fhir:Patient.address [
    fhir:Address.line [
      fhir:value "${escapeTurtleLiteral(data.address?.calle)}"
    ] ;
    fhir:Address.postalCode [
      fhir:value "${escapeTurtleLiteral(data.address?.cp)}"
    ] ;
    fhir:Address.city [
      fhir:value "${escapeTurtleLiteral(data.address?.ciudad)}"
    ] ;
    fhir:Address.state [
      fhir:value "${escapeTurtleLiteral(data.address?.provincia)}"
    ] ;
    fhir:Address.country [
      fhir:value "${escapeTurtleLiteral(data.address?.pais)}"
    ]
  ] .
`
}

async function savePatient(payload) {
  const turtle = buildPatientPatchTurtle(payload)
  await api.patch(`/mis_pacientes/${props.patient_id}/actualizar`, turtle)
}

async function confirmSave() {
  try {
    showSaveConfirm.value = false

    const payload = JSON.parse(JSON.stringify(edited))
    await savePatient(payload)

    Object.assign(patient, payload)
    patient.address = { ...payload.address }

    isEditing.value = false
    showSavedMessage.value = true
  } catch (e) {
    console.error(e)
    error.value = 'No se pudieron guardar los cambios'
  }
}

function cancelEdit() {
  Object.assign(patient, JSON.parse(JSON.stringify(original.value)))
  isEditing.value = false
  showSaveConfirm.value = false
}

async function fetchPatientDatos() {
  try {
    error.value = ''
    resetPatient()
    isEditing.value = false
    showSaveConfirm.value = false

    const { data: rows } = await api.get(`/mis_pacientes/${props.patient_id}/get/datos`)

    if (!rows.length) {
      error.value = 'No se encontraron datos del paciente'
      return
    }

    const row = rows[0]

    patient.nombre = row.nombre || ''
    patient.apellido = row.apellidos || ''
    patient.genero = row.genero || ''
    patient.fecha_nacimiento = row.fechaNacimiento || ''
    patient.estado_civil = row.estado_civil || ''
    patient.telefono = row.telefono || ''
    patient.ssn = row.ss || ''
    patient.address.calle = row.calle || ''
    patient.address.cp = row.cp || ''
    patient.address.ciudad = row.ciudad || ''
    patient.address.provincia = row.provincia || ''
    patient.address.pais = row.pais || ''
  } catch (e) {
    error.value =
      e.response?.data?.detail ||
      'Error al cargar datos (revisa token o permisos)'
    console.error(e)
  }
}

function goProcedures() {
  if (isEditing.value) return
  router.push(`/patient/${props.patient_id}/procedimientos`)
}

function goAllergies() {
  if (isEditing.value) return
  router.push(`/patient/${props.patient_id}/alergias`)
}

function doExport() {
  if (isEditing.value) return
  window.open(`${api.defaults.baseURL}/export_all/${props.patient_id}`, '_blank')
}

onMounted(fetchPatientDatos)

watch(
  () => props.patient_id,
  async (newId, oldId) => {
    if (!newId || newId === oldId) return
    await fetchPatientDatos()
  }
)
</script>

<style scoped>

.avatar {
  width: 70px;
  height: 70px;
  color: #3b82f6;
  background: #eff6ff;
  padding: 12px;
  border-radius: 50%;
}

.header {
  display: flex;
  flex-direction: column;   /* clave */
  align-items: center;
  justify-content: center;
  text-align: center;
  margin-bottom: 1rem;
}

.name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2937;
  margin-top: 0.4rem;
}
/* CONTENEDOR PRINCIPAL */
.patient-container {
  display: flex;
  gap: 1.5rem;
  padding: 1.2rem;
  max-width: 1100px;
  margin: 0 auto;
}

/* COLUMNA IZQUIERDA */
.patient-main {
  flex: 1;
  background: #ffffff;
  border-radius: 10px;
  padding: 1.2rem;
  border: 1px solid #e5e7eb;
}

/* COLUMNA DERECHA */
.actions {
  width: 220px;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

/* TÍTULO */
.patient-main h2 {
  margin-bottom: 0.8rem;
  font-size: 1.3rem;
  color: #1f2937;
}

/* CAMPOS */
.patient-main p {
  margin: 0.3rem 0;
  font-size: 0.9rem;
  color: #374151;
}

.patient-main strong {
  color: #111827;
}

/* BOTONES BASE */
.btn {
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.7rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: 0.15s ease;
}

/* COLORES BOTONES */
.edit-btn {
  background: #e0f2fe;
  color: #0369a1;
}

.edit-btn:hover {
  background: #bae6fd;
}

.save-btn {
  background: #22c55e;
  color: white;
}

.save-btn:hover {
  background: #16a34a;
}

.cancel-btn {
  background: #ef4444;
  color: white;
}

.cancel-btn:hover {
  background: #dc2626;
}

.secondary {
  background: #f3f4f6;
  color: #374151;
}

.secondary:hover {
  background: #e5e7eb;
}

.primary {
  background: #3b82f6;
  color: white;
}

.primary:hover {
  background: #2563eb;
}

/* DESHABILITADO */
.actions .btn:disabled {
  opacity: 0.5;
  pointer-events: none;
}

/* EDICIÓN */
.edit-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.8rem;
}

/* CAMPOS EDITABLES */
[contenteditable="true"] {
  background: #f9fafb;
  border-bottom: 1px dashed #9ca3af;
  padding: 1px 3px;
}

/* MODAL (más compacto) */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-box {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  min-width: 260px;
  max-width: 90vw;
}

.modal-box h3 {
  margin: 0 0 0.4rem;
  font-size: 1rem;
  color: #1f2937;
}

.modal-box p {
  font-size: 0.85rem;
  color: #4b5563;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.4rem;
  margin-top: 0.7rem;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .patient-container {
    flex-direction: column;
  }

  .actions {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
  }
}
</style>
