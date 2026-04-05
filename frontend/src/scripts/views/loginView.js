import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'
import { buildUrlEncodedForm, normalizeLoginError, saveSessionToken } from '@/scripts/shared/session'

export function useLoginView() {
  const router = useRouter()
  const email = ref('')
  const password = ref('')
  const showPassword = ref(false)
  const error = ref('')

  const login = async () => {
    error.value = ''

    try {
      const params = buildUrlEncodedForm({
        email: email.value,
        password: password.value
      })

      const res = await api.post('/login/', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })

      saveSessionToken(res.data.access_token)
      router.push('/profile')
    } catch (loginError) {
      const normalizedError = normalizeLoginError(loginError)

      if (normalizedError === 'password') {
        password.value = ''
        showPassword.value = false
        error.value = 'Contraseña incorrecta'
        return
      }

      if (normalizedError === 'user-not-found') {
        error.value = 'No existe ningún usuario con ese email'
        return
      }

      error.value = normalizedError
    }
  }

  return {
    email,
    password,
    showPassword,
    error,
    login
  }
}
