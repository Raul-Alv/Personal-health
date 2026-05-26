import axios from 'axios'
import router from '../router'
import { clearStoredToken, getValidToken } from '@/utils/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

export function setApiToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common.Authorization
  }
}

export function clearAuthSession(redirectTo = null) {
  clearStoredToken()
  setApiToken(null)

  if (redirectTo && router.currentRoute.value.name !== redirectTo.name) {
    router.push(redirectTo)
  }
}

setApiToken(getValidToken())

api.interceptors.request.use(config => {
  const token = getValidToken()

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  } else {
    delete config.headers.Authorization
  }

  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    const status = err.response?.status
    const detail = err.response?.data?.detail?.toLowerCase?.() || ''
    const userMissing = status === 404 && detail.includes('usuario no encontrado')

    if (status === 401 || userMissing) {
      clearAuthSession({ name: 'Login' })
    }

    return Promise.reject(err)
  }
)

export default api
