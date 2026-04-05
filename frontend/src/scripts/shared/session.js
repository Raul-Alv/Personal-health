import { onMounted, onUnmounted, ref } from 'vue'
import { clearAuthSession, setApiToken } from '@/api/axios'
import { getValidToken } from '@/utils/auth'

const AUTH_SESSION_EVENT = 'auth-session-changed'

function emitSessionChange() {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(AUTH_SESSION_EVENT))
}

export function saveSessionToken(token) {
  localStorage.setItem('token', token)
  setApiToken(token)
  emitSessionChange()
}

export function clearSession(redirectTo = { name: 'Login' }) {
  clearAuthSession(redirectTo)
  emitSessionChange()
}

export function buildUrlEncodedForm(fields) {
  const params = new URLSearchParams()

  Object.entries(fields).forEach(([key, value]) => {
    params.append(key, value ?? '')
  })

  return params
}

export function normalizeLoginError(error) {
  const detail = error.response?.data?.detail || ''
  const normalizedDetail = detail.toLowerCase()

  if (normalizedDetail.includes('contrase')) {
    return 'password'
  }

  if (normalizedDetail.includes('usuario no encontrado')) {
    return 'user-not-found'
  }

  return detail || 'Error en el login'
}

export function useSessionToken() {
  const token = ref(getValidToken())

  const syncToken = () => {
    token.value = getValidToken()
    setApiToken(token.value)
  }

  onMounted(() => {
    if (typeof window === 'undefined') return
    window.addEventListener('storage', syncToken)
    window.addEventListener(AUTH_SESSION_EVENT, syncToken)
  })

  onUnmounted(() => {
    if (typeof window === 'undefined') return
    window.removeEventListener('storage', syncToken)
    window.removeEventListener(AUTH_SESSION_EVENT, syncToken)
  })

  return {
    token,
    syncToken
  }
}
