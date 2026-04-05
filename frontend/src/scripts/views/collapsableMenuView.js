import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/axios'
import { clearSession, useSessionToken } from '@/scripts/shared/session'

export function useCollapsableMenuView() {
  const router = useRouter()
  const route = useRoute()

  const pacientes = ref([])
  const pacienteAbierto = ref(null)
  const { token } = useSessionToken()

  const currentPatientId = computed(() => {
    return route.params.patient_id || route.params.id || route.params.patientId || null
  })

  const cargarPacientes = async () => {
    if (!token.value) {
      pacientes.value = []
      pacienteAbierto.value = null
      return
    }

    try {
      const { data } = await api.get('/mis_pacientes/menu')
      pacientes.value = data

      if (currentPatientId.value) {
        pacienteAbierto.value = currentPatientId.value
      }
    } catch (error) {
      pacientes.value = []
      console.error('Error cargando pacientes:', error)
    }
  }

  const togglePaciente = async (id) => {
    const yaEstabaAbierto = pacienteAbierto.value === id
    pacienteAbierto.value = yaEstabaAbierto ? null : id

    if (!yaEstabaAbierto) {
      await router.push(`/patient/${id}`)
    }
  }

  const navegar = (id, seccion) => {
    if (!seccion) {
      router.push(`/patient/${id}`)
      return
    }

    router.push(`/patient/${id}/${seccion}`)
  }

  const navegarExportar = (patientId) => {
    if (patientId) {
      router.push('/export/')
      return
    }

    alert('Por favor, selecciona un paciente primero')
  }

  const navegarImportar = (patientId) => {
    if (patientId) {
      router.push('/import/')
      return
    }

    alert('Por favor, selecciona un paciente primero')
  }

  const navegarHome = () => {
    router.push('/profile')
  }

  const cerrarSesion = () => {
    clearSession({ name: 'Login' })
  }

  onMounted(cargarPacientes)

  watch(
    () => currentPatientId.value,
    (newPatientId) => {
      if (newPatientId) {
        pacienteAbierto.value = newPatientId
      }
    },
    { immediate: true }
  )

  watch(
    () => route.fullPath,
    () => {
      if (currentPatientId.value) {
        pacienteAbierto.value = currentPatientId.value
      }
    }
  )

  watch(token, (newToken) => {
    if (newToken) {
      cargarPacientes()
      return
    }

    pacientes.value = []
    pacienteAbierto.value = null
  })

  return {
    pacientes,
    pacienteAbierto,
    togglePaciente,
    navegar,
    navegarExportar,
    navegarImportar,
    navegarHome,
    cerrarSesion
  }
}
