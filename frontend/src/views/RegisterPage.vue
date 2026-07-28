<template>
  <div class="register-page">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow">
          <div class="card-body p-4">
            <h3 class="card-title text-center mb-4">
              <i class="bi bi-person-plus me-2"></i>Register
            </h3>

            <!-- Alerts -->
            <div v-if="error" class="alert alert-danger alert-dismissible fade show">
              {{ error }}
              <button type="button" class="btn-close" @click="error = ''"></button>
            </div>
            <div v-if="success" class="alert alert-success">{{ success }}</div>

            <form @submit.prevent="handleRegister">
              <!-- Role selector -->
              <div class="mb-3">
                <label class="form-label">I am a</label>
                <select v-model="role" class="form-select" required>
                  <option value="">-- Select Role --</option>
                  <option value="student">Student</option>
                  <option value="company">Company</option>
                </select>
              </div>

              <!-- Common fields -->
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input v-model="username" type="text" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="email" type="email" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="password" type="password" class="form-control"
                       minlength="4" required>
              </div>

              <!-- Student-specific fields -->
              <template v-if="role === 'student'">
                <div class="mb-3">
                  <label class="form-label">Full Name</label>
                  <input v-model="name" type="text" class="form-control" required>
                </div>
                <div class="row">
                  <div class="col-md-4 mb-3">
                    <label class="form-label">Branch</label>
                    <input v-model="branch" type="text" class="form-control"
                           placeholder="e.g. CSE" required>
                  </div>
                  <div class="col-md-4 mb-3">
                    <label class="form-label">CGPA</label>
                    <input v-model.number="cgpa" type="number" step="0.01"
                           min="0" max="10" class="form-control" required>
                  </div>
                  <div class="col-md-4 mb-3">
                    <label class="form-label">Year</label>
                    <input v-model.number="year" type="number" min="1" max="5"
                           class="form-control" required>
                  </div>
                </div>
              </template>

              <!-- Company-specific fields -->
              <template v-if="role === 'company'">
                <div class="mb-3">
                  <label class="form-label">Company Name</label>
                  <input v-model="company_name" type="text" class="form-control" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">HR Contact</label>
                  <input v-model="hr_contact" type="text" class="form-control" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Website</label>
                  <input v-model="website" type="url" class="form-control"
                         placeholder="https://example.com" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Description</label>
                  <textarea v-model="description" class="form-control" rows="3" required></textarea>
                </div>
              </template>

              <button type="submit" class="btn btn-success w-100" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                Register
              </button>
            </form>

            <p class="text-center mt-3 mb-0">
              Already have an account?
              <router-link to="/login">Login here</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API = 'http://localhost:5000/api'

export default {
  name: 'RegisterPage',
  data() {
    return {
      role: '', username: '', email: '', password: '',
      // Student
      name: '', branch: '', cgpa: 0, year: 1,
      // Company
      company_name: '', hr_contact: '', website: '', description: '',
      error: '', success: '', loading: false
    }
  },
  methods: {
    async handleRegister() {
      this.loading = true
      this.error = ''
      this.success = ''

      const payload = {
        username: this.username,
        email: this.email,
        password: this.password,
        role: this.role
      }

      if (this.role === 'student') {
        Object.assign(payload, {
          name: this.name, branch: this.branch,
          cgpa: this.cgpa, year: this.year
        })
      } else if (this.role === 'company') {
        Object.assign(payload, {
          company_name: this.company_name,
          hr_contact: this.hr_contact,
          website: this.website,
          description: this.description
        })
      }

      try {
        const res = await axios.post(`${API}/auth/register`, payload)
        this.success = res.data.msg || 'Registered! You can now login.'
        // Redirect to login after a short delay
        setTimeout(() => this.$router.push('/login'), 1500)
      } catch (err) {
        this.error = err.response?.data?.msg || 'Registration failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>