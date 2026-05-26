import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'
import { clearSession } from '@/scripts/shared/session'

function formatImportValidationErrors(detail) {
  const validation = detail?.validation_errors
  if (!Array.isArray(validation) || !validation.length) {
    return detail?.message || detail || 'No se pudo importar el archivo'
  }

  const summary = validation
    .map((item) => {
      const shape = item?.shape || 'ShEx'
      const focus = item?.focus ? ` [${item.focus}]` : ''
      return `${shape}${focus}: ${item?.reason || 'Error de validacion no especificado.'}`
    })
    .join(' | ')

  return detail?.message ? `${detail.message} ${summary}` : summary
}

export function useProfileView() {
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

  const clearMessages = () => {
    error.value = ''
    success.value = ''
  }

  const clonePatients = (list) => list.map((patient) => ({ ...patient }))

  const resetPasswordModal = () => {
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    passwordError.value = ''
  }

  const resetImportState = () => {
    selectedImportFiles.value = []
    importError.value = ''
    importing.value = false
  }

  const startEdit = () => {
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

  const cancelEdit = () => {
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

  const openPasswordModal = () => {
    resetPasswordModal()
    showPasswordModal.value = true
  }

  const closePasswordModal = () => {
    resetPasswordModal()
    showPasswordModal.value = false
  }

  const confirmPasswordChange = () => {
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

  const askSetDefault = (patient) => {
    pendingDefaultPatient.value = patient
    showDefaultModal.value = true
  }

  const closeDefaultModal = () => {
    pendingDefaultPatient.value = null
    showDefaultModal.value = false
  }

  const confirmSetDefaultPatient = () => {
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

  const openImportModal = () => {
    importError.value = ''
    showImportModal.value = true
  }

  const closeImportModal = (force = false) => {
    if (importing.value && !force) return
    showImportModal.value = false
    resetImportState()
  }

  const handleImportFileChange = (event) => {
    selectedImportFiles.value = Array.from(event.target.files || [])
    importError.value = ''
  }

  const fetchPatients = async () => {
    try {
      const { data } = await api.get('/mis_pacientes/menu')
      patients.value = data || []
    } catch (fetchError) {
      console.error('Error cargando pacientes asociados:', fetchError)
    }
  }

  const confirmImportPatient = async () => {
    if (!selectedImportFiles.value.length) {
      importError.value = 'Debes seleccionar RDF + ShEx, o un ZIP exportado por la aplicacion.'
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
      formData.append('set_as_favorite', String(!patients.value.length))

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
    } catch (importPatientError) {
      importError.value = formatImportValidationErrors(importPatientError.response?.data?.detail)
      console.error(importPatientError)
    } finally {
      importing.value = false
    }
  }

  const fetchUser = async () => {
    try {
      clearMessages()
      const { data } = await api.get('/me/')
      user.nombre = data.nombre || ''
      user.email = data.email || ''
      user.usuario_uri = data.usuario_uri || ''
    } catch (fetchUserError) {
      error.value = fetchUserError.response?.data?.detail || 'Error al cargar el perfil'
      console.error(fetchUserError)
    }
  }

  const saveEdit = async () => {
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
      success.value = 'Perfil actualizado correctamente.'
    } catch (saveError) {
      error.value = saveError.response?.data?.detail || 'No se pudo guardar el perfil'
      console.error(saveError)
    } finally {
      saving.value = false
    }
  }

  const goToPatient = (patientId) => {
    router.push(`/patient/${patientId}`)
  }

  const logout = () => {
    clearSession({ name: 'Login' })
  }

  onMounted(async () => {
    await fetchUser()
    await fetchPatients()
  })

  return {
    user,
    edited,
    patients,
    isEditing,
    saving,
    error,
    success,
    showPasswordModal,
    passwordChanged,
    passwordError,
    showDefaultModal,
    pendingDefaultPatient,
    showImportModal,
    selectedImportFiles,
    importing,
    importError,
    passwordForm,
    defaultPatient,
    otherPatients,
    startEdit,
    cancelEdit,
    openPasswordModal,
    closePasswordModal,
    confirmPasswordChange,
    askSetDefault,
    closeDefaultModal,
    confirmSetDefaultPatient,
    openImportModal,
    closeImportModal,
    handleImportFileChange,
    confirmImportPatient,
    saveEdit,
    goToPatient,
    logout
  }
}
