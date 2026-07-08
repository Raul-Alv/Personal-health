export const PATIENT_MENU_REFRESH_EVENT = 'patient-menu-refresh'

export function emitPatientMenuRefresh() {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(PATIENT_MENU_REFRESH_EVENT))
}
