<template>
  <div class="page">
    <section class="card profile-card">
      <div class="card-header">
        <div>
          <p class="eyebrow">Mi perfil</p>
          <h1>{{ user.nombre || 'Usuario' }}</h1>
        </div>

        <div class="actions">
          <button
            v-if="!isEditing"
            class="btn btn-primary"
            @click="startEdit"
          >
            Editar
          </button>

          <template v-else>
            <button
              class="btn btn-success"
              :disabled="saving"
              @click="saveEdit"
            >
              {{ saving ? 'Guardando...' : 'Guardar' }}
            </button>
            <button
              class="btn btn-secondary"
              :disabled="saving"
              @click="cancelEdit"
            >
              Cancelar
            </button>
          </template>
        </div>
      </div>

      <p v-if="error" class="message message-error">{{ error }}</p>
      <p v-if="success" class="message message-success">{{ success }}</p>

      <div class="profile-grid">
        <div class="form-row">
          <label>Nombre</label>
          <template v-if="isEditing">
            <input v-model="edited.nombre" type="text" class="input" />
          </template>
          <template v-else>
            <div class="value">{{ user.nombre || '-' }}</div>
          </template>
        </div>

        <div class="form-row">
          <label>Email</label>
          <template v-if="isEditing">
            <input v-model="edited.email" type="email" class="input" />
          </template>
          <template v-else>
            <div class="value">{{ user.email || '-' }}</div>
          </template>
        </div>

        <div v-if="isEditing" class="form-row">
          <label>Contraseña</label>
          <button class="btn btn-outline" type="button" @click="openPasswordModal">
            Cambiar contraseña
          </button>
          <small v-if="passwordChanged" class="helper-text success-text">
            Se cambiará la contraseña al guardar el perfil.
          </small>
        </div>
      </div>

      <div v-if="defaultPatient" class="related-section">
        <div class="section-header">
          <h2>Paciente predeterminado</h2>
        </div>

        <button class="default-patient-card" @click="goToPatient(defaultPatient.id)">
          <span class="default-badge">Predeterminado</span>
          <strong>{{ defaultPatient.nombre }} {{ defaultPatient.apellido }}</strong>
        </button>
      </div>

      <div v-if="otherPatients.length || isEditing" class="related-section">
        <div class="section-header">
          <h2>Otros pacientes</h2>
          <p v-if="isEditing" class="section-help">
            Pulsa la estrella para convertir un paciente en predeterminado.
          </p>
        </div>

        <div class="patient-list">
          <div
            v-for="patient in otherPatients"
            :key="patient.id"
            class="patient-item"
          >
            <button
              v-if="isEditing"
              class="star-btn"
              type="button"
              title="Poner como predeterminado"
              @click.stop="askSetDefault(patient)"
            >
              ★
            </button>

            <button
              class="patient-chip"
              @click="goToPatient(patient.id)"
            >
              {{ patient.nombre }} {{ patient.apellido }}
            </button>
          </div>

          <button
            v-if="isEditing"
            class="add-patient-btn"
            type="button"
            title="Importar paciente"
            @click="openImportModal"
          >
            +
          </button>
        </div>
      </div>
    </section>

    <div v-if="showPasswordModal" class="modal-overlay" @click.self="closePasswordModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Cambiar contraseña</h3>
          <button class="modal-close" @click="closePasswordModal">×</button>
        </div>

        <div class="modal-body">
          <div class="form-row">
            <label>Nueva contraseña</label>
            <input
              v-model="passwordForm.newPassword"
              type="password"
              class="input"
              placeholder="Introduce la nueva contraseña"
            />
          </div>

          <div class="form-row">
            <label>Confirmar contraseña</label>
            <input
              v-model="passwordForm.confirmPassword"
              type="password"
              class="input"
              placeholder="Repite la nueva contraseña"
            />
          </div>

          <p v-if="passwordError" class="message message-error">
            {{ passwordError }}
          </p>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="closePasswordModal">
            Cancelar
          </button>
          <button class="btn btn-primary" @click="confirmPasswordChange">
            Confirmar
          </button>
        </div>
      </div>
    </div>

    <div v-if="showDefaultModal && pendingDefaultPatient" class="modal-overlay" @click.self="closeDefaultModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Cambiar paciente predeterminado</h3>
          <button class="modal-close" @click="closeDefaultModal">×</button>
        </div>

        <div class="modal-body">
          <p>
            ¿Quieres poner a
            <strong>{{ pendingDefaultPatient.nombre }} {{ pendingDefaultPatient.apellido }}</strong>
            como perfil predeterminado?
          </p>
          <p v-if="defaultPatient">
            <strong>{{ defaultPatient.nombre }} {{ defaultPatient.apellido }}</strong>
            pasará a la lista de otros pacientes.
          </p>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="closeDefaultModal">
            Cancelar
          </button>
          <button class="btn btn-primary" @click="confirmSetDefaultPatient">
            Aceptar
          </button>
        </div>
      </div>
    </div>

    <div v-if="showImportModal" class="modal-overlay" @click.self="closeImportModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Importar paciente</h3>
          <button class="modal-close" @click="closeImportModal">×</button>
        </div>

        <div class="modal-body">
          <div class="form-row">
            <label>Archivo TTL del paciente</label>
            <input
              class="input"
              type="file"
              accept=".ttl,text/turtle"
              @change="handleImportFileChange"
            />
          </div>

          <p v-if="selectedImportFiles.length" class="helper-text">
            Archivo seleccionado: {{ selectedImportFiles.map(file => file.name).join(', ') }}
          </p>

          <p v-if="importError" class="message message-error">
            {{ importError }}
          </p>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" :disabled="importing" @click="closeImportModal">
            Cancelar
          </button>
          <button
            class="btn btn-primary"
            :disabled="importing || !selectedImportFiles.length"
            @click="confirmImportPatient"
          >
            {{ importing ? 'Importando...' : 'Importar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

const router = useRouter()

const user = reactive({
  nombre: '',
  email: '',
  usuario_uri: ''
})

const edited = reactive({
  nombre: '',
  email: '',
  password: ''
})

const patients = ref([])
const originalPatients = ref([])
const isEditing = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const original = ref({})

const showPasswordModal = ref(false)
const passwordChanged = ref(false)
const passwordError = ref('')

const showDefaultModal = ref(false)
const pendingDefaultPatient = ref(null)
const showImportModal = ref(false)
const selectedImportFiles = ref([])
const importing = ref(false)
const importError = ref('')

const passwordForm = reactive({
  newPassword: '',
  confirmPassword: ''
})

const defaultPatient = computed(() => patients.value[0] || null)
const otherPatients = computed(() => patients.value.slice(1))

function clearMessages() {
  error.value = ''
  success.value = ''
}

function clonePatients(list) {
  return list.map((patient) => ({ ...patient }))
}

function resetPasswordModal() {
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordError.value = ''
}

function startEdit() {
  clearMessages()
  original.value = JSON.parse(JSON.stringify(user))
  originalPatients.value = clonePatients(patients.value)
  edited.nombre = user.nombre
  edited.email = user.email
  edited.password = ''
  passwordChanged.value = false
  pendingDefaultPatient.value = null
  resetPasswordModal()
  resetImportState()
  showImportModal.value = false
  isEditing.value = true
}

function cancelEdit() {
  clearMessages()
  user.nombre = original.value.nombre || ''
  user.email = original.value.email || ''
  patients.value = clonePatients(originalPatients.value)
  edited.password = ''
  passwordChanged.value = false
  pendingDefaultPatient.value = null
  resetPasswordModal()
  resetImportState()
  showImportModal.value = false
  isEditing.value = false
}

function openPasswordModal() {
  resetPasswordModal()
  showPasswordModal.value = true
}

function closePasswordModal() {
  resetPasswordModal()
  showPasswordModal.value = false
}

function confirmPasswordChange() {
  passwordError.value = ''

  if (!passwordForm.newPassword || !passwordForm.confirmPassword) {
    passwordError.value = 'Debes rellenar ambos campos.'
    return
  }

  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = 'Las contraseñas no coinciden.'
    return
  }

  edited.password = passwordForm.newPassword
  passwordChanged.value = true
  showPasswordModal.value = false
  resetPasswordModal()
}

function askSetDefault(patient) {
  pendingDefaultPatient.value = patient
  showDefaultModal.value = true
}

function closeDefaultModal() {
  pendingDefaultPatient.value = null
  showDefaultModal.value = false
}

function confirmSetDefaultPatient() {
  if (!pendingDefaultPatient.value) return

  const selectedId = pendingDefaultPatient.value.id
  const selectedIndex = patients.value.findIndex((patient) => patient.id === selectedId)

  if (selectedIndex <= 0) {
    closeDefaultModal()
    return
  }

  const currentDefault = patients.value[0]
  const selectedPatient = patients.value[selectedIndex]

  patients.value.splice(selectedIndex, 1)
  patients.value[0] = selectedPatient
  patients.value.splice(1, 0, currentDefault)

  success.value = `${selectedPatient.nombre} ${selectedPatient.apellido} ahora es el paciente predeterminado.`
  closeDefaultModal()
}

function resetImportState() {
  selectedImportFiles.value = []
  importError.value = ''
  importing.value = false
}

function openImportModal() {
  importError.value = ''
  showImportModal.value = true
}

function closeImportModal(force = false) {
  if (importing.value && !force) return
  showImportModal.value = false
  resetImportState()
}

function handleImportFileChange(event) {
  const files = Array.from(event.target.files || [])
  selectedImportFiles.value = files
  importError.value = ''
}

async function confirmImportPatient() {
  if (!selectedImportFiles.value.length) {
    importError.value = 'Debes seleccionar un archivo .ttl.'
    return
  }

  try {
    importError.value = ''
    clearMessages()
    importing.value = true

    const formData = new FormData()
    selectedImportFiles.value.forEach((file) => {
      formData.append('files', file)
    })

    const { data } = await api.post('/import/confirm', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    await fetchPatients()
    closeImportModal(true)
    success.value = 'Paciente importado correctamente.'

    if (data?.redirect) {
      const frontendRedirect = data.redirect.replace('/paciente/', '/patient/')
      router.push(frontendRedirect)
    }
  } catch (e) {
    importError.value = e.response?.data?.detail || 'No se pudo importar el archivo'
    console.error(e)
  } finally {
    importing.value = false
  }
}

async function fetchUser() {
  try {
    clearMessages()
    const { data } = await api.get('/me/')
    user.nombre = data.nombre || ''
    user.email = data.email || ''
    user.usuario_uri = data.usuario_uri || ''
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al cargar el perfil'
    console.error(e)
  }
}

async function fetchPatients() {
  try {
    const { data } = await api.get('/mis_pacientes/menu')
    patients.value = data || []
  } catch (e) {
    console.error('Error cargando pacientes asociados:', e)
  }
}

async function saveEdit() {
  try {
    clearMessages()
    saving.value = true

    const payload = {
      nombre: edited.nombre,
      email: edited.email,
      password: edited.password
    }

    await api.patch('/me/', payload)

    user.nombre = edited.nombre
    user.email = edited.email

    isEditing.value = false
    success.value = 'Perfil actualizado correctamente'
  } catch (e) {
    error.value = e.response?.data?.detail || 'No se pudo guardar el perfil'
    console.error(e)
  } finally {
    saving.value = false
  }
}

function goToPatient(patientId) {
  router.push(`/patient/${patientId}`)
}

onMounted(async () => {
  await fetchUser()
  await fetchPatients()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24px;
  background: #f4f6f8;
}

.card {
  max-width: 900px;
  margin: 0 auto;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.card-header,
.section-header,
.modal-header,
.modal-actions,
.actions,
.patient-list {
  display: flex;
  gap: 12px;
}

.card-header,
.section-header,
.modal-header,
.modal-actions {
  justify-content: space-between;
}

.card-header {
  align-items: flex-start;
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: #6c757d;
}

.card-header h1,
.related-section h2,
.modal-header h3 {
  margin: 0;
}

.card-header h1 {
  font-size: 28px;
}

.profile-grid,
.form-row,
.modal-body {
  display: grid;
  gap: 8px;
}

.profile-grid,
.modal-body {
  gap: 16px;
}

.form-row label {
  font-weight: 600;
  color: #344054;
}

.value,
.input {
  width: 100%;
  min-height: 44px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #d0d5dd;
  background: #f8f9fa;
  box-sizing: border-box;
}

.input {
  background: #fff;
  outline: none;
}

.input:focus {
  border-color: #86b7fe;
}

.actions,
.patient-list {
  flex-wrap: wrap;
}

.actions {
  justify-content: flex-end;
}

.btn,
.patient-chip,
.default-patient-card,
.add-patient-btn,
.star-btn {
  border: none;
  cursor: pointer;
  font-weight: 600;
}

.btn {
  border-radius: 8px;
  padding: 10px 14px;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-primary {
  background: #0d6efd;
  color: #fff;
}

.btn-success {
  background: #198754;
  color: #fff;
}

.btn-secondary {
  background: #6c757d;
  color: #fff;
}

.btn-outline {
  background: #fff;
  color: #0d6efd;
  border: 1px solid #0d6efd;
  width: fit-content;
}

.message {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;
}

.message-error {
  background: #fef3f2;
  color: #b42318;
}

.message-success {
  background: #ecfdf3;
  color: #027a48;
}

.helper-text,
.section-help {
  font-size: 14px;
}

.success-text,
.section-help {
  color: #667085;
}

.related-section {
  margin-top: 32px;
}

.default-patient-card {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  padding: 18px;
  border-radius: 12px;
  background: #f8fbff;
  border: 1px solid #cfe2ff;
  text-align: left;
}

.default-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: #0d6efd;
  color: #fff;
  font-size: 12px;
}

.patient-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.patient-chip {
  border: 1px solid #d0d5dd;
  background: #fff;
  border-radius: 999px;
  padding: 10px 14px;
}

.patient-chip:hover,
.default-patient-card:hover {
  background: #f8f9fa;
}

.star-btn {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  background: #e5e7eb;
  color: #6b7280;
  font-size: 18px;
  line-height: 1;
}

.star-btn:hover {
  background: #d1d5db;
}

.add-patient-btn {
  width: 42px;
  height: 42px;
  border-radius: 999px;
  background: #0d6efd;
  color: #fff;
  font-size: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 1000;
}

.modal {
  width: 100%;
  max-width: 480px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
}

.modal-close {
  border: none;
  background: transparent;
  font-size: 24px;
  cursor: pointer;
  line-height: 1;
}

.modal-actions {
  margin-top: 20px;
}

@media (max-width: 640px) {
  .page {
    padding: 16px;
  }

  .card {
    padding: 18px;
  }

  .card-header,
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }

  .actions {
    justify-content: stretch;
  }
}
</style>
