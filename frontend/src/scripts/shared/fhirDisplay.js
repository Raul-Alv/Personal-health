const createLookup = (entries) => Object.fromEntries(entries.map((option) => [option.value, option.label]))

export const genderOptions = [
  { value: 'male', label: 'Masculino' },
  { value: 'female', label: 'Femenino' },
  { value: 'other', label: 'Otro' },
  { value: 'unknown', label: 'Prefiero no responder' }
]

export const maritalStatusOptions = [
  { value: 'A', label: 'Anulado' },
  { value: 'D', label: 'Divorciado' },
  { value: 'I', label: 'Separacion provisional' },
  { value: 'L', label: 'Separado legalmente' },
  { value: 'M', label: 'Casado' },
  { value: 'C', label: 'Union libre' },
  { value: 'P', label: 'Poligamia' },
  { value: 'T', label: 'Pareja de hecho' },
  { value: 'U', label: 'No casado' },
  { value: 'S', label: 'Soltero' },
  { value: 'W', label: 'Viudo' },
  { value: 'UNK', label: 'Desconocido' }
]

export const procedureStatusLabels = {
  preparation: 'Preparacion',
  'in-progress': 'En curso',
  'not-done': 'No realizado',
  'on-hold': 'En espera',
  stopped: 'Interrumpido',
  completed: 'Completado',
  'entered-in-error': 'Introducido por error',
  unknown: 'Desconocido'
}

const genderLabels = createLookup(genderOptions)
const maritalStatusLabels = createLookup(maritalStatusOptions)

const allergyClinicalStatusLabels = {
  active: 'Activa',
  inactive: 'Inactiva',
  resolved: 'Resuelta'
}

const allergyVerificationStatusLabels = {
  unconfirmed: 'No confirmada',
  confirmed: 'Confirmada',
  refuted: 'Descartada',
  'entered-in-error': 'Introducida por error'
}

const allergyCategoryLabels = {
  food: 'Alimentaria',
  medication: 'Medicamento',
  environment: 'Ambiental',
  biologic: 'Biologica'
}

const allergyCriticalityLabels = {
  low: 'Baja',
  high: 'Alta',
  'unable-to-assess': 'No evaluable'
}

const valueLabelsByPreviewKey = {
  'fhir:Patient.gender__fhir:value': genderLabels,
  'fhir:Patient.maritalStatus__fhir:value': maritalStatusLabels,
  'fhir:Patient.maritalStatus__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value': maritalStatusLabels,
  'fhir:Procedure.status__fhir:value': procedureStatusLabels,
  'fhir:AllergyIntolerance.clinicalStatus__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value': allergyClinicalStatusLabels,
  'fhir:AllergyIntolerance.verificationStatus__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value': allergyVerificationStatusLabels,
  'fhir:AllergyIntolerance.category__fhir:value': allergyCategoryLabels,
  'fhir:AllergyIntolerance.criticality__fhir:value': allergyCriticalityLabels
}

const previewKeyPatterns = [
  { pattern: 'fhir:Patient.gender', labels: genderLabels },
  { pattern: 'fhir:Patient.maritalStatus', labels: maritalStatusLabels },
  { pattern: 'fhir:Procedure.status', labels: procedureStatusLabels },
  { pattern: 'fhir:AllergyIntolerance.clinicalStatus', labels: allergyClinicalStatusLabels },
  { pattern: 'fhir:AllergyIntolerance.verificationStatus', labels: allergyVerificationStatusLabels },
  { pattern: 'fhir:AllergyIntolerance.category', labels: allergyCategoryLabels },
  { pattern: 'fhir:AllergyIntolerance.criticality', labels: allergyCriticalityLabels }
]

function formatByLookup(value, labels) {
  if (value === null || value === undefined || value === '') return value

  const rawValue = String(value)
  const normalizedValue = rawValue.trim()
  return labels[normalizedValue] || labels[normalizedValue.toLowerCase()] || labels[normalizedValue.toUpperCase()] || rawValue
}

export function formatPreviewValue(previewKey, value) {
  const labels =
    valueLabelsByPreviewKey[previewKey] ||
    previewKeyPatterns.find(({ pattern }) => previewKey?.includes(pattern))?.labels
  return labels ? formatByLookup(value, labels) : value
}

export function formatProcedureStatus(value) {
  return formatByLookup(value, procedureStatusLabels)
}
