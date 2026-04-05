import { onMounted, ref } from 'vue'
import api from '@/api/axios'

export function useAllergyListPageView(props, emit) {
  const allergies = ref([])
  const loading = ref(false)
  const error = ref(false)

  const loadAllergies = async () => {
    loading.value = true
    error.value = false

    try {
      const resp = await api.get(`/mis_pacientes/${props.patient_id}/get/alergias`)
      allergies.value = resp.data
    } catch (fetchError) {
      console.error(fetchError)
      error.value = true
    } finally {
      loading.value = false
    }
  }

  const selectAllergy = (allergy) => {
    emit('select', allergy)
  }

  onMounted(loadAllergies)

  return {
    allergies,
    loading,
    error,
    selectAllergy
  }
}
