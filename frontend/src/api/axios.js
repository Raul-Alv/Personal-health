import axios from 'axios'

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
export default api
