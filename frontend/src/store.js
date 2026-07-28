import { reactive } from 'vue'

const auth = reactive({
    token: localStorage.getItem('access_token') || '',
    role: localStorage.getItem('role') || '',
    userId: localStorage.getItem('user_id') || ''
})

export function login(token, role, userId) {
    localStorage.setItem('access_token', token)
    localStorage.setItem('role', role)
    localStorage.setItem('user_id', userId)
    auth.token = token
    auth.role = role
    auth.userId = userId
}

export function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('role')
    localStorage.removeItem('user_id')
    auth.token = ''
    auth.role = ''
    auth.userId = ''
}

export default auth