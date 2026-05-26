export function getValidToken() {
  const token = localStorage.getItem('token')
  if (!token || token === 'undefined' || token === 'null' || token.trim() === '') {
    return null
  }
  return token
}

export function clearStoredToken() {
  localStorage.removeItem('token')
}
