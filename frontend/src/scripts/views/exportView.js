import { computed, onMounted, ref } from 'vue'
import api from '@/api/axios'

export function useExportView() {
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
      let filename = `export_${tipoSeleccionado.value}_${selectedPatient.value}.ttl`

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }

      const blob = new Blob([response.data], { type: 'text/turtle' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      seleccionados.value = []
      alert(`Exportación completada: ${filename}`)
    } catch (error) {
      console.error('Error en la exportación:', error)

      if (error.response?.status === 404) {
        alert('No se encontraron los elementos seleccionados.')
        return
      }

      if (error.response?.status === 403) {
        alert('No tienes permisos para exportar datos de este paciente.')
        return
      }

      alert(`Error en la exportación: ${error.response?.data?.detail || error.message}`)
    }
  }

  onMounted(loadPatients)

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
