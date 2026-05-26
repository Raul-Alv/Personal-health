import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'
import { buildUrlEncodedForm, clearSession, saveSessionToken } from '@/scripts/shared/session'

export function useRegisterView() {
  const router = useRouter()
  const email = ref('')
  const name = ref('')
  const password = ref('')
  const confirm = ref('')
  const showPassword = ref(false)
  const showConfirm = ref(false)

  const register = async () => {
    if (password.value !== confirm.value) {
      alert('Las contraseñas no coinciden')
      return
    }

    try {
      clearSession()

      const params = buildUrlEncodedForm({
        email: email.value,
        nombre: name.value,
        password: password.value
      })

      const res = await api.post('/register/', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })

      saveSessionToken(res.data.access_token)
      router.push('/profile')
    } catch (registerError) {
      alert(registerError.response?.data?.detail || 'No se pudo completar el registro.')
    }
  }

  return {
    email,
    name,
    password,
    confirm,
    showPassword,
    showConfirm,
    register
  }
}
