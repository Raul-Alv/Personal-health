import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/axios'

async function extractExportErrorMessage(error) {
  const status = error.response?.status

  if (status === 404) {
    return 'No se encontraron los elementos seleccionados.'
  }

  if (status === 403) {
    return 'No tienes permisos para exportar datos de este paciente.'
  }

  const payload = error.response?.data
  if (payload instanceof Blob) {
    const text = await payload.text()

    try {
      const parsed = JSON.parse(text)
      const detail = parsed?.detail
      if (typeof detail === 'string') return detail
      if (detail?.message) return detail.message
    } catch {
      if (text) return text
    }
  }

  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (detail?.message) return detail.message

  return error.message || 'La exportacion no se pudo completar.'
}

export function useExportView() {
  const route = useRoute()
  const pacientes = ref([])
  const selectedPatient = ref('')
  const procedimientos = ref([])
  const alergias = ref([])
  const procedimientosSeleccionados = ref([])
  const alergiasSeleccionadas = ref([])
  const incluirPaciente = ref(true)

  const totalSeleccionados = computed(() => {
    return procedimientosSeleccionados.value.length + alergiasSeleccionadas.value.length
  })

  const hasExportableItems = computed(() => procedimientos.value.length > 0 || alergias.value.length > 0)

  const getProcedureId = (item, index) => {
    if (item.procedure_uri) return item.procedure_uri.split('/').pop()
    if (item.id) return item.id
    return `procedimiento-${index}`
  }

  const getAllergyId = (item, index) => {
    if (item.alergia_uri) return item.alergia_uri.split('/').pop()
    if (item.id) return item.id
    return `alergia-${index}`
  }

  const formatProcedureLabel = (item, index) => {
    const name = item.text || item.display || item.code || `Procedimiento ${index + 1}`
    const details = [item.code, item.performedDateTime].filter(Boolean).join(' - ')
    return details && details !== name ? `${name} (${details})` : name
  }

  const formatAllergyLabel = (item, index) => {
    const name = item.display || item.text || item.code || `Alergia ${index + 1}`
    const details = [item.code, item.onsetDateTime].filter(Boolean).join(' - ')
    return details && details !== name ? `${name} (${details})` : name
  }

  const clearSelections = () => {
    procedimientosSeleccionados.value = []
    alergiasSeleccionadas.value = []
  }

  const loadPatients = async () => {
    try {
      const res = await api.get('/mis_pacientes/menu')
      pacientes.value = res.data
    } catch (error) {
      console.error('Error cargando pacientes:', error)
      alert('Error al cargar la lista de pacientes')
    }
  }

  const loadPatientData = async () => {
    if (!selectedPatient.value) return

    try {
      clearSelections()
      const resProc = await api.get(`/mis_pacientes/${selectedPatient.value}/get/procedimientos`)
      procedimientos.value = resProc.data

      const resAlerg = await api.get(`/mis_pacientes/${selectedPatient.value}/get/alergias`)
      alergias.value = resAlerg.data
    } catch (error) {
      console.error('Error cargando datos del paciente:', error)
      alert('Error al cargar los datos del paciente')
    }
  }

  const applyInitialSelection = async () => {
    const initialPatientId = typeof route.query.patientId === 'string' ? route.query.patientId : ''

    if (!initialPatientId) return

    selectedPatient.value = initialPatientId
    await loadPatientData()
  }

  const selectAllProcedimientos = () => {
    procedimientosSeleccionados.value = procedimientos.value.map((item, index) => getProcedureId(item, index))
  }

  const deselectAllProcedimientos = () => {
    procedimientosSeleccionados.value = []
  }

  const selectAllAlergias = () => {
    alergiasSeleccionadas.value = alergias.value.map((item, index) => getAllergyId(item, index))
  }

  const deselectAllAlergias = () => {
    alergiasSeleccionadas.value = []
  }

  const selectAll = () => {
    selectAllProcedimientos()
    selectAllAlergias()
  }

  const deselectAll = () => {
    clearSelections()
  }

  const exportarSeleccionados = async () => {
    if (!totalSeleccionados.value) {
      alert('Debes seleccionar al menos un elemento.')
      return
    }

    try {
      const formData = new FormData()
      formData.append('patient_id', selectedPatient.value)
      formData.append('procedure_ids', procedimientosSeleccionados.value.join(','))
      formData.append('allergy_ids', alergiasSeleccionadas.value.join(','))
      formData.append('incluir_paciente', incluirPaciente.value.toString())

      const response = await api.post('/export_seleccionados', formData, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      const contentDisposition = response.headers['content-disposition']
      let filename = `export_seleccion_${selectedPatient.value}.zip`

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }

      const blob = new Blob([response.data], { type: 'application/zip' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      clearSelections()
      alert(`Exportacion completada: ${filename}`)
    } catch (error) {
      console.error('Error en la exportacion:', error)
      alert(await extractExportErrorMessage(error))
    }
  }

  onMounted(async () => {
    await loadPatients()
    await applyInitialSelection()
  })

  return {
    pacientes,
    selectedPatient,
    procedimientos,
    alergias,
    procedimientosSeleccionados,
    alergiasSeleccionadas,
    incluirPaciente,
    totalSeleccionados,
    hasExportableItems,
    getProcedureId,
    getAllergyId,
    formatProcedureLabel,
    formatAllergyLabel,
    loadPatientData,
    selectAllProcedimientos,
    deselectAllProcedimientos,
    selectAllAlergias,
    deselectAllAlergias,
    selectAll,
    deselectAll,
    exportarSeleccionados
  }
}
