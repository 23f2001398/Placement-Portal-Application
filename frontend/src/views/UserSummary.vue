<template>
  <div class="user-summary">
    <h2 class="mb-4"><i class="bi bi-clipboard-data me-2"></i>My Placement Summary</h2>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <template v-else>
      <!-- Stats row -->
      <div class="row mb-4">
        <div class="col-md-3 mb-3">
          <div class="card bg-primary text-white text-center shadow-sm">
            <div class="card-body">
              <h3>{{ totalApplications }}</h3>
              <p class="mb-0 small">Total Applications</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="card bg-info text-white text-center shadow-sm">
            <div class="card-body">
              <h3>{{ shortlisted }}</h3>
              <p class="mb-0 small">Shortlisted</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="card bg-success text-white text-center shadow-sm">
            <div class="card-body">
              <h3>{{ selected }}</h3>
              <p class="mb-0 small">Selected</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="card bg-danger text-white text-center shadow-sm">
            <div class="card-body">
              <h3>{{ rejected }}</h3>
              <p class="mb-0 small">Rejected</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Placement history -->
      <h5 class="mb-3">Placement History</h5>
      <div v-if="history.length === 0" class="text-muted">No placement history yet.</div>
      <table v-else class="table table-bordered table-striped">
        <thead class="table-dark">
          <tr>
            <th>Drive</th><th>Company</th><th>Status</th><th>Applied On</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="h in history" :key="h.id">
            <td>{{ h.drive_title }}</td>
            <td>{{ h.company_name }}</td>
            <td><span class="badge" :class="statusBadge(h.status)">{{ h.status }}</span></td>
            <td>{{ formatDate(h.applied_at) }}</td>
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
  name: 'UserSummary',
  data() {
    return {
      applications: [],
      history: [],
      loading: true
    }
  },
  computed: {
    headers() {
      return { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    },
    totalApplications() { return this.applications.length },
    shortlisted() { return this.applications.filter(a => a.status === 'shortlisted').length },
    selected() { return this.applications.filter(a => a.status === 'selected').length },
    rejected() { return this.applications.filter(a => a.status === 'rejected').length }
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const [aRes, hRes] = await Promise.all([
          axios.get(`${API}/student/applications`, { headers: this.headers }),
          axios.get(`${API}/student/history`, { headers: this.headers })
        ])
        this.applications = aRes.data.applications || []
        this.history = hRes.data.history || []
      } catch {}
      this.loading = false
    },
    statusBadge(s) {
      return {
        applied: 'bg-secondary', shortlisted: 'bg-info text-dark',
        interview_scheduled: 'bg-primary', selected: 'bg-success',
        rejected: 'bg-danger', cancelled: 'bg-dark'
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