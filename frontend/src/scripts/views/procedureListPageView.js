import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

export function useProcedureListPageView(props) {
  const procedures = ref([])
  const loading = ref(false)
  const error = ref(false)
  const filters = reactive({
    nombre: '',
    fecha: '',
    practicante: '',
    diente: ''
  })
  const showingFilteredResults = ref(false)
  const router = useRouter()

  const getProcedureId = (procedure) => procedure.procedure_uri.split('/').pop()
  const hasActiveFilters = computed(() =>
    Object.values(filters).some((value) => value.trim() !== '')
  )

  const loadProcedures = async () => {
    loading.value = true
    error.value = false

    try {
      const resp = await api.get(`/mis_pacientes/${props.patient_id}/get/procedimientos`)
      procedures.value = resp.data
    } catch (fetchError) {
      console.error(fetchError)
      error.value = true
    } finally {
      loading.value = false
    }
  }

  const buildFilterParams = () => {
    const params = {}

    Object.entries(filters).forEach(([key, value]) => {
      const trimmedValue = value.trim()
      if (trimmedValue) {
        params[key] = trimmedValue
      }
    })

    return params
  }

  const applyFilters = async () => {
    const params = buildFilterParams()

    if (!Object.keys(params).length) {
      showingFilteredResults.value = false
      await loadProcedures()
      return
    }

    loading.value = true
    error.value = false

    try {
      const resp = await api.get(`/mis_pacientes/${props.patient_id}/search/procedimientos`, { params })
      procedures.value = resp.data
      showingFilteredResults.value = true
    } catch (fetchError) {
      console.error(fetchError)
      error.value = true
    } finally {
      loading.value = false
    }
  }

  const clearFilters = async () => {
    filters.nombre = ''
    filters.fecha = ''
    filters.practicante = ''
    filters.diente = ''
    showingFilteredResults.value = false
    await loadProcedures()
  }

  const deleteProcedure = async (procedure) => {
    if (!confirm('¿Seguro que quieres eliminar este procedimiento?')) return

    try {
      await api.delete(`/mis_pacientes/${props.patient_id}/delete/procedimientos/${getProcedureId(procedure)}`)
      procedures.value = procedures.value.filter(
        (currentProcedure) => currentProcedure.procedure_uri !== procedure.procedure_uri
      )
    } catch (deleteError) {
      alert('No se pudo eliminar el procedimiento.')
      console.error(deleteError)
    }
  }

  const selectProcedure = (procedure) => {
    router.push(`/patient/${props.patient_id}/procedimientos/${getProcedureId(procedure)}`)
  }

  onMounted(loadProcedures)

  return {
    procedures,
    loading,
    error,
    filters,
    hasActiveFilters,
    showingFilteredResults,
    applyFilters,
    clearFilters,
    deleteProcedure,
    selectProcedure
  }
}
