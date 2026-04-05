import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

export function useProcedureListPageView(props) {
  const procedures = ref([])
  const loading = ref(false)
  const error = ref(false)
  const router = useRouter()

  const getProcedureId = (procedure) => procedure.procedure_uri.split('/').pop()

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

  const deleteProcedure = async (procedure) => {
    if (!confirm('Seguro que quieres eliminar este procedimiento?')) return

    try {
      await api.delete(`/mis_pacientes/${props.patient_id}/delete/procedimientos/${getProcedureId(procedure)}`)
      procedures.value = procedures.value.filter((currentProcedure) => currentProcedure.id !== procedure.id)
    } catch (deleteError) {
      alert('Error al eliminar')
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
    deleteProcedure,
    selectProcedure
  }
}
