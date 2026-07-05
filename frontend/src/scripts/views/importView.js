import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'
import { formatPreviewValue } from '@/scripts/shared/fhirDisplay'

const prefixMap = {
  'http://hl7.org/fhir/': 'fhir:',
  'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf:',
  'http://www.w3.org/2001/XMLSchema#': 'xsd:',
  'http://example.org/fhir/custom#': 'ex:'
}

const etiquetas = {
  'fhir:Patient.name__fhir:HumanName.given__fhir:value': 'Nombre',
  'fhir:Patient.name__fhir:HumanName.family__fhir:value': 'Apellidos',
  'fhir:Patient.birthDate__fhir:value': 'Fecha de nacimiento',
  'fhir:Patient.gender__fhir:value': 'Genero',
  'fhir:Patient.identifier__fhir:Identifier.value__fhir:value': 'Identificador',
  'fhir:Patient.address__fhir:Address.city__fhir:value': 'Ciudad',
  'fhir:Patient.address__fhir:Address.line__fhir:value': 'Direccion',
  'fhir:Patient.address__fhir:Address.postalCode__fhir:value': 'Codigo postal',
  'fhir:Patient.telecom__fhir:ContactPoint.value__fhir:value': 'Telefono o correo electronico',
  'fhir:Patient.maritalStatus__fhir:value': 'Estado civil',
  'fhir:Patient.maritalStatus__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value': 'Estado civil',
  'fhir:AllergyIntolerance.code__fhir:CodeableConcept.coding__fhir:Coding.display__fhir:value': 'Alergia',
  'fhir:AllergyIntolerance.code__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value': 'Codigo',
  'fhir:AllergyIntolerance.onsetDateTime__fhir:value': 'Fecha de inicio',
  'fhir:AllergyIntolerance.patient__fhir:Reference.reference__fhir:value': 'Paciente',
  'fhir:AllergyIntolerance.actor__fhir:Reference.reference__fhir:value': 'Profesional',
  'fhir:AllergyIntolerance.recorder__fhir:Reference.reference__fhir:value': 'Profesional',
  'fhir:AllergyIntolerance.asserter__fhir:Reference.reference__fhir:value': 'Profesional',
  'fhir:AllergyIntolerance.clinicalStatus__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value': 'Estado clinico',
  'fhir:AllergyIntolerance.category__fhir:value': 'Categoria',
  'fhir:Procedure.code__fhir:CodeableConcept.coding__fhir:Coding.display__fhir:value': 'Procedimiento',
  'fhir:Procedure.code__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value': 'Codigo procedimiento',
  'fhir:Procedure.code__fhir:CodeableConcept.text__fhir:value': 'Texto procedimiento',
  'fhir:Procedure.performedDateTime__fhir:value': 'Fecha del procedimiento',
  'fhir:Procedure.subject__fhir:Reference.reference__fhir:value': 'Paciente',
  'fhir:Procedure.performer__fhir:Procedure.performer.actor__fhir:Reference.reference__fhir:value': 'Profesional',
  'fhir:Procedure.note__fhir:Annotation.text__fhir:value': 'Notas',
  'fhir:AllergyIntolerance.verificationStatus__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value': 'Estado de verificacion',
  'fhir:AllergyIntolerance.criticality__fhir:value': 'Criticidad',
  'fhir:AllergyIntolerance.note__fhir:Annotation.text__fhir:value': 'Notas',
  'fhir:Procedure.status': 'Estado del procedimiento',
  'fhir:Procedure.status__fhir:value': 'Estado del procedimiento'
}

const etiquetaPatterns = [
  { pattern: 'fhir:Patient.gender', etiqueta: 'Genero' },
  { pattern: 'fhir:Patient.maritalStatus', etiqueta: 'Estado civil' },
  { pattern: 'fhir:Procedure.status', etiqueta: 'Estado del procedimiento' },
  { pattern: 'fhir:AllergyIntolerance.clinicalStatus', etiqueta: 'Estado clinico' },
  { pattern: 'fhir:AllergyIntolerance.verificationStatus', etiqueta: 'Estado de verificacion' },
  { pattern: 'fhir:AllergyIntolerance.category', etiqueta: 'Categoria' },
  { pattern: 'fhir:AllergyIntolerance.criticality', etiqueta: 'Criticidad' }
]

function abreviarClave(clave) {
  if (!clave || typeof clave !== 'string') return ''

  let abreviada = clave
  for (const [url, prefijo] of Object.entries(prefixMap)) {
    abreviada = abreviada.replaceAll(url, prefijo)
  }

  return abreviada
}

function obtenerEtiqueta(claveAbreviada) {
  return (
    etiquetas[claveAbreviada] ||
    etiquetaPatterns.find(({ pattern }) => claveAbreviada.includes(pattern))?.etiqueta
  )
}

function formatValidationError(errorItem) {
  const foco = errorItem?.focus ? ` [${errorItem.focus}]` : ''
  const shape = errorItem?.shape || 'ShEx'
  const reason = errorItem?.reason || 'Error de validacion no especificado.'
  return `${shape}${foco}: ${reason}`
}

export function useImportView() {
  const files = ref([])
  const preview = ref([])
  const validationErrors = ref([])
  const router = useRouter()

  const extractImportErrorMessage = (error, fallbackMessage) => {
    const detail = error.response?.data?.detail
    const validation = detail?.validation_errors

    if (Array.isArray(validation) && validation.length) {
      validationErrors.value = validation.map(formatValidationError)
      return detail?.message || 'Se han detectado errores de validacion RDF/ShEx.'
    }

    validationErrors.value = []
    return detail?.message || detail || fallbackMessage
  }

  const filtrarDatos = (datos) => {
    return Object.entries(datos)
      .filter(([clave]) => obtenerEtiqueta(abreviarClave(clave)))
      .map(([clave, valor]) => {
        const claveAbreviada = abreviarClave(clave)
        return {
          etiqueta: obtenerEtiqueta(claveAbreviada),
          valor: formatPreviewValue(claveAbreviada, valor)
        }
      })
  }

  const onFileChange = (event) => {
    files.value = Array.from(event.target.files || [])
    preview.value = []
    validationErrors.value = []
  }

  const previewFiles = async () => {
    try {
      validationErrors.value = []
      const form = new FormData()
      files.value.forEach((file) => form.append('files', file))

      const { data } = await api.post('/import/preview', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      preview.value = data
    } catch (error) {
      console.error('Error al generar la vista previa:', error)
      preview.value = []
      alert(
        extractImportErrorMessage(
          error,
          'No se pudo generar la vista previa de los archivos seleccionados.'
        )
      )
    }
  }

  const confirmImport = async () => {
    try {
      validationErrors.value = []
      const form = new FormData()
      files.value.forEach((file) => form.append('files', file))

      const { data } = await api.post('/import/confirm', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      if (Array.isArray(data.warnings) && data.warnings.length) {
        alert(data.warnings.join('\n'))
      }

      router.push(data.redirect.replace('/paciente/', '/patient/'))
    } catch (error) {
      console.error('Error al confirmar la importacion:', error)
      alert(extractImportErrorMessage(error, 'La importacion no se pudo completar.'))
    }
  }

  return {
    files,
    preview,
    validationErrors,
    filtrarDatos,
    onFileChange,
    previewFiles,
    confirmImport
  }
}
