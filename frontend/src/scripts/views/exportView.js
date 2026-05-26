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
  const tipoSeleccionado = ref('')
  const seleccionados = ref([])
  const incluirPaciente = ref(true)

  const itemsMostrados = computed(() => {
    return tipoSeleccionado.value === 'procedimientos' ? procedimientos.value : alergias.value
  })

  const getItemId = (item, index) => {
    if (item.procedure_uri) return item.procedure_uri.split('/').pop()
    if (item.alergia_uri) return item.alergia_uri.split('/').pop()
    if (item.id) return item.id
    return `${tipoSeleccionado.value}-${index}`
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
    const initialType = typeof route.query.tipo === 'string' ? route.query.tipo : ''

    if (!initialPatientId) return

    selectedPatient.value = initialPatientId
    await loadPatientData()

    if (initialType === 'procedimientos' && procedimientos.value.length) {
      setTipo('procedimientos')
      return
    }

    if (initialType === 'alergias' && alergias.value.length) {
      setTipo('alergias')
    }
  }

  const setTipo = (tipo) => {
    tipoSeleccionado.value = tipo
    seleccionados.value = []
  }

  const selectAll = () => {
    seleccionados.value = itemsMostrados.value.map((item, index) => getItemId(item, index))
  }

  const deselectAll = () => {
    seleccionados.value = []
  }

  const exportarSeleccionados = async () => {
    if (!seleccionados.value.length) {
      alert('Debes seleccionar al menos un elemento.')
      return
    }

    try {
      const formData = new FormData()
      formData.append('patient_id', selectedPatient.value)
      formData.append('tipo', tipoSeleccionado.value)
      formData.append('ids', seleccionados.value.join(','))
      formData.append('incluir_paciente', incluirPaciente.value.toString())

      const response = await api.post('/export_seleccionados', formData, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      const contentDisposition = response.headers['content-disposition']
      let filename = `export_${tipoSeleccionado.value}_${selectedPatient.value}.zip`

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

      seleccionados.value = []
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
    tipoSeleccionado,
    seleccionados,
    incluirPaciente,
    itemsMostrados,
    getItemId,
    loadPatientData,
    setTipo,
    selectAll,
    deselectAll,
    exportarSeleccionados
  }
}
