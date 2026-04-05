import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

const genderOptions = [
  { value: 'male', label: 'Masculino' },
  { value: 'female', label: 'Femenino' },
  { value: 'other', label: 'Otro' },
  { value: 'unknown', label: 'Prefiero no responder' }
]

const maritalStatusOptions = [
  { value: 'A', label: 'Anulado' },
  { value: 'D', label: 'Divorciado' },
  { value: 'I', label: 'Interlocutorio' },
  { value: 'L', label: 'Legalmente separado' },
  { value: 'M', label: 'Casado' },
  { value: 'C', label: 'Ley común' },
  { value: 'P', label: 'Poligamia' },
  { value: 'T', label: 'Pareja de hecho' },
  { value: 'U', label: 'Sin contrato nupcial' },
  { value: 'S', label: 'Soltero' },
  { value: 'W', label: 'Viudo/a' }
]

const genderLabels = Object.fromEntries(genderOptions.map((option) => [option.value, option.label]))
const maritalStatusLabels = Object.fromEntries(maritalStatusOptions.map((option) => [option.value, option.label]))

function createAddress() {
  return {
    calle: '',
    cp: '',
    ciudad: '',
    provincia: '',
    pais: ''
  }
}

function createPatientState() {
  return {
    nombre: '',
    apellido: '',
    genero: '',
    fecha_nacimiento: '',
    estado_civil: '',
    telefono: '',
    ssn: '',
    address: createAddress()
  }
}

function escapeTurtleLiteral(value) {
  return String(value ?? '')
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\r/g, '\\r')
    .replace(/\n/g, '\\n')
}

function buildPatientPatchTurtle(patientId, data) {
  const patientUri = `http://hl7.org/fhir/Patient/${patientId}`

  return `@prefix fhir: <http://hl7.org/fhir/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<${patientUri}>
  fhir:Patient.gender [
    fhir:value "${escapeTurtleLiteral(data.genero)}"
  ] ;
  fhir:Patient.birthDate [
    fhir:value "${escapeTurtleLiteral(data.fecha_nacimiento)}"
  ] ;
  fhir:Patient.maritalStatus [
    fhir:value "${escapeTurtleLiteral(data.estado_civil)}"
  ] ;
  fhir:Patient.identifier [
    fhir:Identifier.value [
      fhir:value "${escapeTurtleLiteral(data.ssn)}"
    ]
  ] ;
  fhir:Patient.telecom [
    fhir:ContactPoint.value [
      fhir:value "${escapeTurtleLiteral(data.telefono)}"
    ]
  ] ;
  fhir:Patient.address [
    fhir:Address.line [
      fhir:value "${escapeTurtleLiteral(data.address?.calle)}"
    ] ;
    fhir:Address.postalCode [
      fhir:value "${escapeTurtleLiteral(data.address?.cp)}"
    ] ;
    fhir:Address.city [
      fhir:value "${escapeTurtleLiteral(data.address?.ciudad)}"
    ] ;
    fhir:Address.state [
      fhir:value "${escapeTurtleLiteral(data.address?.provincia)}"
    ] ;
    fhir:Address.country [
      fhir:value "${escapeTurtleLiteral(data.address?.pais)}"
    ]
  ] .
`
}

export function usePatientView(props) {
  const router = useRouter()

  const patient = reactive(createPatientState())
  const edited = reactive(createPatientState())
  const showSSN = ref(false)
  const error = ref('')
  const isEditing = ref(false)
  const showSaveConfirm = ref(false)
  const showSavedMessage = ref(false)
  const original = ref({})

  const maskedSSN = computed(() => (patient.ssn || '').replace(/.(?=.{4})/g, '*'))
  const genderLabel = computed(() => genderLabels[patient.genero] || patient.genero || '')
  const maritalStatusLabel = computed(() => maritalStatusLabels[patient.estado_civil] || patient.estado_civil || '')

  const fillEditedFromPatient = () => {
    edited.nombre = patient.nombre
    edited.apellido = patient.apellido
    edited.genero = patient.genero
    edited.fecha_nacimiento = patient.fecha_nacimiento
    edited.estado_civil = patient.estado_civil
    edited.telefono = patient.telefono
    edited.ssn = patient.ssn
    edited.address = {
      calle: patient.address.calle,
      cp: patient.address.cp,
      ciudad: patient.address.ciudad,
      provincia: patient.address.provincia,
      pais: patient.address.pais
    }
  }

  const resetPatient = () => {
    Object.assign(patient, createPatientState())
  }

  const startEdit = () => {
    original.value = JSON.parse(JSON.stringify(patient))
    fillEditedFromPatient()
    isEditing.value = true
  }

  const openConfirmSave = () => {
    showSaveConfirm.value = true
  }

  const onInput = (field, event) => {
    const value = event.target.innerText.trim()
    const addressFields = ['calle', 'cp', 'ciudad', 'provincia', 'pais']

    if (addressFields.includes(field)) {
      edited.address[field] = value
      return
    }

    edited[field] = value
  }

  const savePatient = async (payload) => {
    const turtle = buildPatientPatchTurtle(props.patient_id, payload)
    await api.patch(`/mis_pacientes/${props.patient_id}/actualizar`, turtle)
  }

  const confirmSave = async () => {
    try {
      showSaveConfirm.value = false

      const payload = JSON.parse(JSON.stringify(edited))
      await savePatient(payload)

      Object.assign(patient, payload)
      patient.address = { ...payload.address }

      isEditing.value = false
      showSavedMessage.value = true
    } catch (saveError) {
      console.error(saveError)
      error.value = 'No se pudieron guardar los cambios'
    }
  }

  const cancelEdit = () => {
    Object.assign(patient, JSON.parse(JSON.stringify(original.value)))
    isEditing.value = false
    showSaveConfirm.value = false
  }

  const fetchPatientDatos = async () => {
    try {
      error.value = ''
      resetPatient()
      isEditing.value = false
      showSaveConfirm.value = false

      const { data: rows } = await api.get(`/mis_pacientes/${props.patient_id}/get/datos`)

      if (!rows.length) {
        error.value = 'No se encontraron datos del paciente'
        return
      }

      const row = rows[0]

      patient.nombre = row.nombre || ''
      patient.apellido = row.apellidos || ''
      patient.genero = row.genero || ''
      patient.fecha_nacimiento = row.fechaNacimiento || ''
      patient.estado_civil = row.estado_civil || ''
      patient.telefono = row.telefono || ''
      patient.ssn = row.ss || ''
      patient.address.calle = row.calle || ''
      patient.address.cp = row.cp || ''
      patient.address.ciudad = row.ciudad || ''
      patient.address.provincia = row.provincia || ''
      patient.address.pais = row.pais || ''
    } catch (fetchError) {
      error.value = fetchError.response?.data?.detail || 'Error al cargar datos (revisa token o permisos)'
      console.error(fetchError)
    }
  }

  const goProcedures = () => {
    if (isEditing.value) return
    router.push(`/patient/${props.patient_id}/procedimientos`)
  }

  const goAllergies = () => {
    if (isEditing.value) return
    router.push(`/patient/${props.patient_id}/alergias`)
  }

  const doExport = () => {
    if (isEditing.value) return
    window.open(`${api.defaults.baseURL}/export_all/${props.patient_id}`, '_blank')
  }

  onMounted(fetchPatientDatos)

  watch(
    () => props.patient_id,
    async (newId, oldId) => {
      if (!newId || newId === oldId) return
      await fetchPatientDatos()
    }
  )

  return {
    genderOptions,
    maritalStatusOptions,
    patient,
    edited,
    showSSN,
    error,
    isEditing,
    showSaveConfirm,
    showSavedMessage,
    maskedSSN,
    genderLabel,
    maritalStatusLabel,
    startEdit,
    openConfirmSave,
    onInput,
    confirmSave,
    cancelEdit,
    goProcedures,
    goAllergies,
    doExport
  }
}
