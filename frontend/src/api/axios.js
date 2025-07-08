import axios from 'axios'
import router from '../router'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

const token = localStorage.getItem('token')
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}
api.interceptors.request.use(config => {
  console.log(
    `➡️ Petición Axios: [${config.method.toUpperCase()}]`,
    config.baseURL + config.url
  );
  return config;
});

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      router.push({ name: 'Login' })
    }
    return Promise.reject(err)
  }
)
export default api
