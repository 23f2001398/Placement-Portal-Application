<template>
  <div class="admin-summary">
    <h2 class="mb-4"><i class="bi bi-bar-chart me-2"></i>Admin Summary</h2>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <template v-else>
      <!-- Summary cards -->
      <div class="row mb-4">
        <div class="col-md-3 mb-3" v-for="(item, idx) in cards" :key="idx">
          <div class="card shadow-sm border-0" :class="item.bg">
            <div class="card-body text-center text-white">
              <i :class="item.icon" class="display-6"></i>
              <h3 class="mt-2">{{ item.value }}</h3>
              <p class="mb-0 small">{{ item.label }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent applications table -->
      <h5 class="mb-3">Recent Applications</h5>
      <div v-if="applications.length === 0" class="text-muted">No applications yet.</div>
      <table v-else class="table table-bordered table-striped">
        <thead class="table-dark">
          <tr>
            <th>ID</th><th>Student</th><th>Drive</th><th>Company</th>
            <th>Status</th><th>Applied</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in applications" :key="a.id">
            <td>{{ a.id }}</td>
            <td>{{ a.student_id }}</td>
            <td>{{ a.drive_title }}</td>
            <td>{{ a.company_name }}</td>
            <td>
              <span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span>
            </td>
            <td>{{ formatDate(a.applied_at) }}</td>
          </tr>
        </tbody>
      </table>
    </template>
  </div>
</template>

<script>
import axios from 'axios'

const API = 'http://localhost:5000/api'

export default {
  name: 'AdminSummary',
  data() {
    return {
      summary: {},
      applications: [],
      loading: true
    }
  },
  computed: {
    headers() {
      return { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    },
    cards() {
      const s = this.summary
      return [
        { label: 'Total Students', value: s.total_students || 0,
          icon: 'bi bi-people', bg: 'bg-primary' },
        { label: 'Total Companies', value: s.total_companies || 0,
          icon: 'bi bi-buildings', bg: 'bg-success' },
        { label: 'Total Drives', value: s.total_drives || 0,
          icon: 'bi bi-briefcase', bg: 'bg-info' },
        { label: 'Selected', value: s.selected_students || 0,
          icon: 'bi bi-check-circle', bg: 'bg-warning' }
      ]
    }
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const [sumRes, appRes] = await Promise.all([
          axios.get(`${API}/admin/summary`, { headers: this.headers }),
          axios.get(`${API}/admin/applications`, { headers: this.headers })
        ])
        this.summary = sumRes.data.summary || {}
        this.applications = (appRes.data.applications || []).slice(0, 20)
      } catch {}
      this.loading = false
    },
    statusBadge(s) {
      return {
        applied: 'bg-secondary',
        shortlisted: 'bg-info text-dark',
        interview_scheduled: 'bg-primary',
        selected: 'bg-success',
        rejected: 'bg-danger',
        cancelled: 'bg-dark'
      }[s] || 'bg-secondary'
    },
    formatDate(iso) {
      if (!iso) return '—'
      return new Date(iso).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric'
      })
    }
  },
  mounted() {
    this.loadData()
  }
}
</script>