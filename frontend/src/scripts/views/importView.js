import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

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
  'fhir:Patient.gender__fhir:value': 'Género',
  'fhir:Patient.identifier__fhir:Identifier.value__fhir:value': 'Identificador',
  'fhir:Patient.address__fhir:Address.city__fhir:value': 'Ciudad',
  'fhir:Patient.address__fhir:Address.line__fhir:value': 'Dirección',
  'fhir:Patient.address__fhir:Address.postalCode__fhir:value': 'Código postal',
  'fhir:Patient.telecom__fhir:ContactPoint.value__fhir:value': 'Teléfono/Email',
  'fhir:AllergyIntolerance.code__fhir:CodeableConcept.coding__fhir:Coding.display__fhir:value': 'Alergia',
  'fhir:AllergyIntolerance.code__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value': 'Código',
  'fhir:AllergyIntolerance.onsetDateTime__fhir:value': 'Fecha de inicio',
  'fhir:AllergyIntolerance.patient__fhir:Reference.reference__fhir:value': 'Paciente',
  'fhir:AllergyIntolerance.actor__fhir:Reference.reference__fhir:value': 'Profesional',
  'fhir:AllergyIntolerance.category__fhir:value': 'Categoría',
  'fhir:Procedure.code__fhir:CodeableConcept.coding__fhir:Coding.display__fhir:value': 'Procedimiento',
  'fhir:Procedure.code__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value': 'Código procedimiento',
  'fhir:Procedure.code__fhir:CodeableConcept.text__fhir:value': 'Texto procedimiento',
  'fhir:Procedure.performedDateTime__fhir:value': 'Fecha del procedimiento',
  'fhir:Procedure.subject__fhir:Reference.reference__fhir:value': 'Paciente',
  'fhir:Procedure.performer__fhir:Procedure.performer.actor__fhir:Reference.reference__fhir:value': 'Profesional',
  'fhir:AllergyIntolerance.verificationStatus__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value': 'Estado de verificación',
  'fhir:AllergyIntolerance.criticality__fhir:value': 'Criticidad',
  'fhir:AllergyIntolerance.note__fhir:Annotation.text__fhir:value': 'Notas',
  'fhir:Procedure.status__fhir:value': 'Estado del procedimiento'
}

function abreviarClave(clave) {
  if (!clave || typeof clave !== 'string') return ''

  let abreviada = clave
  for (const [url, prefijo] of Object.entries(prefixMap)) {
    abreviada = abreviada.replaceAll(url, prefijo)
  }

  return abreviada
}

export function useImportView() {
  const files = ref([])
  const preview = ref([])
  const router = useRouter()

  const filtrarDatos = (datos) => {
    return Object.entries(datos)
      .filter(([clave]) => etiquetas[abreviarClave(clave)])
      .map(([clave, valor]) => ({
        etiqueta: etiquetas[abreviarClave(clave)],
        valor
      }))
  }

  const onFileChange = (event) => {
    files.value = Array.from(event.target.files)
    preview.value = []
  }

  const previewFiles = async () => {
    const form = new FormData()
    files.value.forEach((file) => form.append('files', file))

    const { data } = await api.post('/import/preview', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    preview.value = data
    console.log('Preview completa:', data)

    preview.value.forEach((item) => {
      Object.keys(item.datos).forEach((clave) => {
        const abrev = abreviarClave(clave)
        console.log('Abreviada:', abrev, '| Original:', clave)
        console.log('Etiqueta:', etiquetas[abrev] || 'No encontrada')
        console.log('Valor:', item.datos[clave] || 'No encontrado')
        console.log('-----------------------------')
      })

      console.log('Item completo:', item.datos)
    })
  }

  const confirmImport = async () => {
    const form = new FormData()
    files.value.forEach((file) => form.append('files', file))

    const { data } = await api.post('/import/confirm', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    router.push(data.redirect)
  }

  return {
    files,
    preview,
    filtrarDatos,
    onFileChange,
    previewFiles,
    confirmImport
  }
}
