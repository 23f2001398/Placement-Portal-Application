<template>
  <div class="admin-panel">
    <h2 class="mb-4"><i class="bi bi-shield-lock me-2"></i>Admin Dashboard</h2>

    <!-- Summary cards -->
    <div class="row mb-4">
      <div class="col-md-3" v-for="(val, label) in summaryCards" :key="label">
        <div class="card text-white bg-primary mb-3 shadow-sm">
          <div class="card-body text-center">
            <h5 class="card-title">{{ val }}</h5>
            <p class="card-text small">{{ label }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-3">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: tab === 'companies' }"
           href="#" @click.prevent="tab = 'companies'; loadPendingCompanies()">
          Pending Companies
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: tab === 'drives' }"
           href="#" @click.prevent="tab = 'drives'; loadPendingDrives()">
          Pending Drives
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: tab === 'alldrives' }"
           href="#" @click.prevent="tab = 'alldrives'; loadAllDrives()">
          All Drives
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: tab === 'users' }"
           href="#" @click.prevent="tab = 'users'; loadUsers()">
          All Users
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: tab === 'search' }"
           href="#" @click.prevent="tab = 'search'">
          Search
        </a>
      </li>
    </ul>

    <!-- PENDING COMPANIES -->
    <div v-if="tab === 'companies'">
      <div v-if="pendingCompanies.length === 0" class="text-muted">No pending companies.</div>
      <table v-else class="table table-bordered table-hover">
        <thead class="table-light">
          <tr>
            <th>ID</th><th>Company Name</th><th>HR Contact</th><th>Website</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in pendingCompanies" :key="c.id">
            <td>{{ c.id }}</td>
            <td>{{ c.company_name }}</td>
            <td>{{ c.hr_contact }}</td>
            <td>{{ c.website }}</td>
            <td>
              <button class="btn btn-sm btn-success me-1" @click="approveCompany(c.id, 'approved')">
                Approve
              </button>
              <button class="btn btn-sm btn-danger" @click="approveCompany(c.id, 'rejected')">
                Reject
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- PENDING DRIVES -->
    <div v-if="tab === 'drives'">
      <div v-if="pendingDrives.length === 0" class="text-muted">No pending drives.</div>
      <table v-else class="table table-bordered table-hover">
        <thead class="table-light">
          <tr>
            <th>ID</th><th>Job Title</th><th>Company</th><th>Deadline</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in pendingDrives" :key="d.id">
            <td>{{ d.id }}</td>
            <td>{{ d.job_title }}</td>
            <td>{{ d.company_name }}</td>
            <td>{{ formatDate(d.deadline) }}</td>
            <td>
              <button class="btn btn-sm btn-success me-1" @click="approveDrive(d.id, 'approved')">
                Approve
              </button>
              <button class="btn btn-sm btn-danger" @click="approveDrive(d.id, 'rejected')">
                Reject
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ALL DRIVES -->
    <div v-if="tab === 'alldrives'">
      <div v-if="allDrives.length === 0" class="text-muted">No drives found.</div>
      <table v-else class="table table-bordered table-hover">
        <thead class="table-light">
          <tr>
            <th>ID</th><th>Company</th><th>Role / Position</th><th>Applicants</th>
            <th>Deadline</th><th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in allDrives" :key="d.id">
            <td>{{ d.id }}</td>
            <td>{{ d.company_name }}</td>
            <td>{{ d.job_title }}</td>
            <td><span class="badge bg-primary">{{ d.application_count || 0 }}</span></td>
            <td>{{ formatDate(d.deadline) }}</td>
            <td>
              <span class="badge" :class="statusBadge(d.status)">{{ d.status }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ALL USERS -->
    <div v-if="tab === 'users'">
      <table class="table table-bordered table-hover">
        <thead class="table-light">
          <tr>
            <th>ID</th><th>Username</th><th>Email</th><th>Role</th><th>Status</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.username }}</td>
            <td>{{ u.email }}</td>
            <td><span class="badge" :class="roleBadge(u.role)">{{ u.role }}</span></td>
            <td>
              <span class="badge" :class="userStatusBadge(u)">{{ userStatusText(u) }}</span>
            </td>
            <td>
              <button v-if="u.role !== 'admin'" class="btn btn-sm"
                :class="u.is_active ? 'btn-warning' : 'btn-outline-success'"
                @click="toggleBlacklist(u.id, u.is_active)">
                {{ u.is_active ? 'Blacklist' : 'Restore' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- SEARCH -->
    <div v-if="tab === 'search'">
      <div class="input-group mb-3">
        <input v-model="searchQuery" type="text" class="form-control"
               placeholder="Search by username, company name, student name..."
               @keyup.enter="doSearch">
        <button class="btn btn-primary" @click="doSearch">Search</button>
      </div>

      <div v-if="searchResults">
        <h6>Users</h6>
        <ul class="list-group mb-3">
          <li v-for="u in searchResults.users" :key="'u'+u.id" class="list-group-item">
            {{ u.username }} ({{ u.role }}) — {{ u.email }}
          </li>
          <li v-if="searchResults.users.length === 0" class="list-group-item text-muted">
            No matching users
          </li>
        </ul>
        <h6>Companies</h6>
        <ul class="list-group mb-3">
          <li v-for="c in searchResults.companies" :key="'c'+c.id" class="list-group-item">
            {{ c.company_name }} — Status: {{ c.approval_status }}
          </li>
          <li v-if="searchResults.companies.length === 0" class="list-group-item text-muted">
            No matching companies
          </li>
        </ul>
        <h6>Students</h6>
        <ul class="list-group mb-3">
          <li v-for="s in searchResults.students" :key="'s'+s.id" class="list-group-item">
            {{ s.name }} — Branch: {{ s.branch }}, CGPA: {{ s.cgpa }}
          </li>
          <li v-if="searchResults.students.length === 0" class="list-group-item text-muted">
            No matching students
          </li>
        </ul>
      </div>
    </div>

    <!-- Feedback -->
    <div v-if="feedback" class="alert mt-3" :class="feedbackOk ? 'alert-success' : 'alert-danger'">
      {{ feedback }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API = 'http://localhost:5000/api'

export default {
  name: 'AdminPanel',
  data() {
    return {
      tab: 'companies',
      summary: {},
      pendingCompanies: [],
      pendingDrives: [],
      allDrives: [],
      users: [],
      searchQuery: '',
      searchResults: null,
      feedback: '',
      feedbackOk: true,
      refreshTimer: null
    }
  },
  computed: {
    headers() {
      return { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    },
    summaryCards() {
      const s = this.summary
      return {
        'Students': s.total_students || 0,
        'Companies': s.total_companies || 0,
        'Drives': s.total_drives || 0,
        'Applications': s.total_applications || 0
      }
    }
  },
  methods: {
    async loadSummary() {
      try {
        const res = await axios.get(`${API}/admin/summary`, { headers: this.headers })
        this.summary = res.data.summary || {}
      } catch {}
    },
    async loadPendingCompanies() {
      try {
        const res = await axios.get(`${API}/admin/pending-companies`, { headers: this.headers })
        this.pendingCompanies = res.data.companies || []
      } catch { this.pendingCompanies = [] }
    },
    async loadPendingDrives() {
      try {
        const res = await axios.get(`${API}/admin/pending-drives`, { headers: this.headers })
        this.pendingDrives = res.data.drives || []
      } catch { this.pendingDrives = [] }
    },
    async loadUsers() {
      try {
        const res = await axios.get(`${API}/admin/users`, { headers: this.headers })
        this.users = res.data.users || []
      } catch { this.users = [] }
    },
    async loadAllDrives() {
      try {
        const res = await axios.get(`${API}/admin/drives`, { headers: this.headers })
        this.allDrives = res.data.drives || []
      } catch { this.allDrives = [] }
    },
    async approveCompany(id, action) {
      try {
        await axios.put(`${API}/admin/approve-company/${id}`, { action }, { headers: this.headers })
        this.showFeedback(`Company ${action}`, true)
        this.loadPendingCompanies()
        this.loadSummary()
      } catch (err) {
        this.showFeedback(err.response?.data?.msg || 'Error', false)
      }
    },
    async approveDrive(id, action) {
      try {
        await axios.put(`${API}/admin/approve-drive/${id}`, { action }, { headers: this.headers })
        this.showFeedback(`Drive ${action}`, true)
        this.loadPendingDrives()
        this.loadSummary()
      } catch (err) {
        this.showFeedback(err.response?.data?.msg || 'Error', false)
      }
    },
    async toggleBlacklist(userId, isActive) {
      const action = isActive ? 'blacklist' : 'restore'
      try {
        await axios.put(`${API}/admin/blacklist/${userId}`, { action }, { headers: this.headers })
        this.showFeedback(`User ${action}ed`, true)
        this.loadUsers()
        this.loadSummary()
      } catch (err) {
        this.showFeedback(err.response?.data?.msg || 'Error', false)
      }
    },
    async doSearch() {
      if (!this.searchQuery.trim()) return
      try {
        const res = await axios.get(`${API}/admin/search`, {
          headers: this.headers,
          params: { q: this.searchQuery }
        })
        this.searchResults = res.data.results || {}
      } catch { this.searchResults = { users: [], companies: [], students: [] } }
    },
    showFeedback(msg, ok) {
      this.feedback = msg
      this.feedbackOk = ok
      setTimeout(() => { this.feedback = '' }, 3000)
    },
    roleBadge(role) {
      return {
        admin: 'bg-danger',
        company: 'bg-info text-dark',
        student: 'bg-success'
      }[role] || 'bg-secondary'
    },
    formatDate(iso) {
      if (!iso) return '—'
      return new Date(iso).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric'
      })
    },
    statusBadge(status) {
      return {
        approved: 'bg-success',
        pending: 'bg-warning text-dark',
        rejected: 'bg-danger',
        closed: 'bg-secondary'
      }[status] || 'bg-secondary'
    },
    userStatusText(u) {
      if (!u.is_active) return 'Blacklisted'
      if (u.role === 'admin') return 'Active'
      if (u.role === 'company') return u.approval_status || 'Active'
      return 'Active'
    },
    userStatusBadge(u) {
      if (!u.is_active) return 'bg-danger'
      if (u.role === 'company') {
        return this.statusBadge(u.approval_status || 'approved')
      }
      return 'bg-success'
    }
  },
  mounted() {
    this.loadSummary()
    this.loadPendingCompanies()
    this.refreshTimer = setInterval(() => {
      this.loadSummary()
      if (this.tab === 'companies') this.loadPendingCompanies()
      else if (this.tab === 'drives') this.loadPendingDrives()
      else if (this.tab === 'alldrives') this.loadAllDrives()
      else if (this.tab === 'users') this.loadUsers()
    }, 10000)
  },
  beforeUnmount() {
    if (this.refreshTimer) clearInterval(this.refreshTimer)
  }
}
</script>
