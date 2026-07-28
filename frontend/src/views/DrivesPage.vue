<template>
  <div class="drives-page">
    <div class="text-center mb-4">
      <h2><i class="bi bi-building me-2"></i>Approved Placement Drives</h2>
      <p class="text-muted">Browse open placement opportunities</p>
    </div>

    <!-- Search & Filters -->
    <div class="card mb-4 shadow-sm">
      <div class="card-body">
         <div class="row g-2">
            <div class="col-md-5">
               <input v-model="searchQuery" type="text" class="form-control"
                      placeholder="Search by job title or company...">
            </div>
            <div class="col-md-3">
               <select v-model="filterBranch" class="form-select">
                  <option value="">All Branches</option>
                  <option value="CSE">CSE</option>
                  <option value="ECE">ECE</option>
                  <option value="EE">EE</option>
                  <option value="ME">ME</option>
                  <option value="CE">CE</option>
               </select>
            </div>
            <div class="col-md-2">
               <select v-model.number="filterYear" class="form-select">
                  <option value="">All Years</option>
                  <option value="1">1st Year</option>
                  <option value="2">2nd Year</option>
                  <option value="3">3rd Year</option>
                  <option value="4">4th Year</option>
               </select>
            </div>
            <div class="col-md-2">
               <input v-model.number="filterCGPA" type="number" 
                      class="form-control" placeholder="Min CGPA" step="0.1" min="0" max="10">
            </div>
         </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <!-- No drives -->
    <div v-else-if="filteredDrives.length === 0" class="text-center py-5 text-muted">
      <i class="bi bi-inbox display-4"></i>
      <p class="mt-2">No placement drives available right now.</p>
    </div>

    <!-- Drive cards -->
    <div v-else class="row">
      <div v-for="drive in filteredDrives" :key="drive.id" class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <h5 class="card-title">{{ drive.job_title }}</h5>
            <h6 class="card-subtitle mb-2 text-primary">{{ drive.company_name }}</h6>
            <p class="card-text text-muted small">{{ drive.description || 'No description' }}</p>

            <ul class="list-unstyled small">
              <li><strong>Branch:</strong> {{ drive.eligibility_branch || 'All' }}</li>
              <li><strong>Min CGPA:</strong> {{ drive.eligibility_cgpa || 'N/A' }}</li>
              <li><strong>Min Year:</strong> {{ drive.eligibility_year || 'Any' }}</li>
              <li><strong>Deadline:</strong>
                <span :class="isExpired(drive.deadline) ? 'text-danger' : 'text-success'">
                  {{ formatDate(drive.deadline) }}
                </span>
              </li>
            </ul>
          </div>
          <div class="card-footer bg-white" v-if="role === 'student'">
            <button v-if="hasApplied(drive.id)" class="btn btn-sm btn-success w-100" disabled>
              <i class="bi bi-check-circle me-1"></i>Applied
            </button>
            <div v-else-if="applyingDrive === drive.id" class="mb-2">
              <label class="form-label small">Upload Resume (PDF) <span class="text-danger">*</span></label>
              <input type="file" class="form-control form-control-sm mb-2" accept="application/pdf"
                     @change="resumeFile = $event.target.files[0]" required>
              <button class="btn btn-sm btn-primary w-100" @click="submitApplication(drive.id)"
                      :disabled="!resumeFile || applying === drive.id">
                <span v-if="applying === drive.id" class="spinner-border spinner-border-sm me-1"></span>
                Submit Application
              </button>
            </div>
            <button v-else class="btn btn-sm btn-outline-primary w-100"
                    @click="applyingDrive = drive.id; resumeFile = null">
              Apply Now
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Feedback  -->
    <div v-if="feedback" class="position-fixed bottom-0 end-0 p-3" style="z-index: 1050">
      <div class="toast show" :class="feedbackType === 'success' ? 'bg-success' : 'bg-danger'"
           style="color: white">
        <div class="toast-body">{{ feedback }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API = 'http://localhost:5000/api'

export default {
  name: 'DrivesPage',
  data() {
    return {
      drives: [],
      searchQuery: '',
      filterBranch: '',
      filterYear: '',
      filterCGPA: '',
      loading: true,
      applying: null,
      applyingDrive: null,
      resumeFile: null,
      feedback: '',
      feedbackType: 'success',
      refreshTimer: null,
      appliedDriveIds: []
    }
  },
  computed: {
    role() { return localStorage.getItem('role') || '' },
    token() { return localStorage.getItem('access_token') || '' },
    filteredDrives() {
      const q = this.searchQuery.toLowerCase()
      const branch = this.filterBranch.toLowerCase()
      
      return this.drives.filter(d => {
         const matchesSearch = !q || d.job_title.toLowerCase().includes(q) || (d.company_name || '').toLowerCase().includes(q)

         let matchesBranch = true
         if (branch && d.eligibility_branch) {
             const allowed = d.eligibility_branch.toLowerCase().split(',').map(s=>s.trim())
             matchesBranch = allowed.includes('all') || allowed.includes(branch)
         }

         const matchesYear = !this.filterYear || !d.eligibility_year || d.eligibility_year === this.filterYear
         
         const matchesCGPA = !this.filterCGPA || (d.eligibility_cgpa || 0) <= this.filterCGPA
         
         return matchesSearch && matchesBranch && matchesYear && matchesCGPA
      })
    }
  },
  methods: {
    hasApplied(driveId) {
      return this.appliedDriveIds.includes(driveId)
    },
    async fetchAppliedDrives() {
      if (this.role !== 'student' || !this.token) return
      try {
        const res = await axios.get(`${API}/student/applied-drives`, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.appliedDriveIds = res.data.applied_drive_ids || []
      } catch {
        this.appliedDriveIds = []
      }
    },
    async fetchDrives() {
      this.loading = true
      try {
        const headers = this.token ? { Authorization: `Bearer ${this.token}` } : {}
        const res = await axios.get(`${API}/drives`, { headers })
        this.drives = res.data.drives || []
      } catch {
        this.drives = []
      } finally {
        this.loading = false
      }
    },
    async submitApplication(driveId) {
      this.applying = driveId
      this.feedback = ''
      try {
        const formData = new FormData()
        formData.append('drive_id', driveId)
        if (this.resumeFile) {
          formData.append('resume', this.resumeFile)
        }
        const res = await axios.post(`${API}/applications`, formData, {
          headers: {
            Authorization: `Bearer ${this.token}`,
            'Content-Type': 'multipart/form-data'
          }
        })
        this.feedback = res.data.msg || 'Applied!'
        this.feedbackType = 'success'
        this.appliedDriveIds.push(driveId)
        this.applyingDrive = null
        this.resumeFile = null
      } catch (err) {
        this.feedback = err.response?.data?.msg || 'Application failed'
        this.feedbackType = 'error'
      } finally {
        this.applying = null
        setTimeout(() => { this.feedback = '' }, 3000)
      }
    },
    formatDate(iso) {
      if (!iso) return 'No deadline'
      return new Date(iso).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric'
      })
    },
    isExpired(iso) {
      if (!iso) return false
      return new Date(iso) < new Date()
    }
  },
  mounted() {
    this.fetchDrives()
    this.fetchAppliedDrives()
    this.refreshTimer = setInterval(() => { this.fetchDrives() }, 10000)
  },
  beforeUnmount() {
    if (this.refreshTimer) clearInterval(this.refreshTimer)
  }
}
</script>