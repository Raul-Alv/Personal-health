import axios from 'axios'
import router from '../router'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

function getValidToken() {
  const token = localStorage.getItem('token')
  if (!token || token === 'undefined' || token === 'null' || token.trim() === '') {
    return null
  }
  return token
}

export function setApiToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common.Authorization
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
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      setApiToken(null)

      if (router.currentRoute.value.name !== 'Login') {
        router.push({ name: 'Login' })
      }
    }

    return Promise.reject(err)
  }
)

export default api