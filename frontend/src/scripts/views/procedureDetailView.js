import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import dentalSvgMarkup from '@/assets/Human_dental_arches.svg?raw'
import api from '@/api/axios'

export { dentalSvgMarkup }

export function useProcedureDetailView(props) {
  const router = useRouter()

  const icono = ref(null)
  const procedures = ref([])
  const confirmDelete = ref(false)

  const activeTeeth = computed(() => {
    const toothCodes = procedures.value
      .map((procedure) => String(procedure?.dienteCode ?? '').trim())
      .filter(Boolean)

    return [...new Set(toothCodes)]
  })

  const hasDentalData = computed(() => activeTeeth.value.length > 0)

  const getSvgRoot = () => icono.value?.querySelector('svg') ?? null

  const paintTeeth = async () => {
    await nextTick()

    const svgRoot = getSvgRoot()
    if (!svgRoot?.querySelectorAll) return

    for (const toothPath of svgRoot.querySelectorAll('path[class]')) {
      toothPath.style.fill = 'none'
      toothPath.style.fillOpacity = '1'
    }

    for (const toothCode of activeTeeth.value) {
      const matches = svgRoot.getElementsByClassName(toothCode)

      for (const toothPath of matches) {
        toothPath.style.fill = 'rgba(255, 0, 0, 0.45)'
        toothPath.style.fillOpacity = '1'
      }
    }
  }

  const fetchTooth = async () => {
    try {
      const resp = await api.get(
        `/mis_pacientes/${props.patient_id}/get/procedimientos/${props.procedure_id}`
      )
      procedures.value = resp.data
    } catch (fetchError) {
      console.error(fetchError)
    }
  }

  const onExport = () => {
    router.push({
      path: '/export/',
      query: {
        patientId: String(props.patient_id),
        tipo: 'procedimientos'
      }
    })
  }

  const goBack = () => {
    router.push(`/patient/${props.patient_id}/procedimientos`)
  }

  const onDelete = async () => {
    try {
      await api.delete(`/mis_pacientes/${props.patient_id}/delete/procedimientos/${props.procedure_id}`)
      goBack()
    } catch (deleteError) {
      console.error('Error al eliminar el procedimiento:', deleteError)
    } finally {
      confirmDelete.value = false
    }
  }

  onMounted(fetchTooth)
  watch(activeTeeth, paintTeeth)

  return {
    icono,
    dentalSvgMarkup,
    procedures,
    activeTeeth,
    hasDentalData,
    confirmDelete,
    onExport,
    onDelete,
    goBack
  }
}
