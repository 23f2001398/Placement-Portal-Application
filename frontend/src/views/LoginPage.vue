<template>
  <div class="login-page">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow">
          <div class="card-body p-4">
            <h3 class="card-title text-center mb-4">
              <i class="bi bi-person-lock me-2"></i>Login
            </h3>

            <!-- Alert -->
            <div v-if="error" class="alert alert-danger alert-dismissible fade show">
              {{ error }}
              <button type="button" class="btn-close" @click="error = ''"></button>
            </div>

            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input v-model="username" type="text" class="form-control"
                       placeholder="Enter username" required>
              </div>

              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="password" type="password" class="form-control"
                       placeholder="Enter password" required>
              </div>

              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                Login
              </button>
            </form>

            <p class="text-center mt-3 mb-0">
              Don't have an account?
              <router-link to="/register">Register here</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { login } from '../store'

const API = 'http://localhost:5000/api'

export default {
  name: 'LoginPage',
  data() {
    return { username: '', password: '', error: '', loading: false }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''
      try {
        const res = await axios.post(`${API}/auth/login`, {
          username: this.username,
          password: this.password
        })

        login(res.data.access_token, res.data.role, res.data.user_id)

        if (res.data.role === 'admin') {
          this.$router.push('/admin')
        } else {
          this.$router.push('/dashboard')
        }
      } catch (err) {
        this.error = err.response?.data?.msg || 'Login failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>