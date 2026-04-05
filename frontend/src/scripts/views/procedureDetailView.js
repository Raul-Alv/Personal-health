import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import DentaduraIconoSvg from '@/assets/Human_dental_arches.svg?component'
import api from '@/api/axios'

export { DentaduraIconoSvg }

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

  const getSvgRoot = () => icono.value?.$el ?? icono.value

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

  const onExport = () => {}

  const goBack = () => {
    router.push(`/patient/${props.patient_id}/procedimientos`)
  }

  const onDelete = async () => {
    try {
      await api.delete(`/mis_pacientes/${props.patient_id}/delete/procedimientos/${props.procedure_id}`)
      goBack()
    } catch (deleteError) {
      console.error('Error al borrar el procedimiento:', deleteError)
    } finally {
      confirmDelete.value = false
    }
  }

  onMounted(fetchTooth)
  watch(activeTeeth, paintTeeth)

  return {
    icono,
    procedures,
    activeTeeth,
    hasDentalData,
    confirmDelete,
    onExport,
    onDelete,
    goBack
  }
}
