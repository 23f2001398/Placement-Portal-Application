<template>
  <div class="user-panel">
    <!--STUDENT DASHBOARD-->
    <template v-if="role === 'student'">
      <h2 class="mb-4"><i class="bi bi-mortarboard me-2"></i>Student Dashboard</h2>

      <!-- Profile card -->
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-primary text-white">
          <i class="bi bi-person-circle me-1"></i> My Profile
          <button class="btn btn-sm btn-light float-end" @click="editingProfile = !editingProfile">
            {{ editingProfile ? 'Cancel' : 'Edit' }}
          </button>
        </div>
        <div class="card-body">
          <form v-if="editingProfile" @submit.prevent="updateStudentProfile">
            <div class="row">
              <div class="col-md-4 mb-2">
                <label class="form-label">Name</label>
                <input v-model="profile.name" class="form-control" required>
              </div>
              <div class="col-md-3 mb-2">
                <label class="form-label">Branch</label>
                <input v-model="profile.branch" class="form-control" required>
              </div>
              <div class="col-md-2 mb-2">
                <label class="form-label">CGPA</label>
                <input v-model.number="profile.cgpa" type="number" step="0.01" class="form-control" required>
              </div>
              <div class="col-md-2 mb-2">
                <label class="form-label">Year</label>
                <input v-model.number="profile.year" type="number" class="form-control" required>
              </div>
              <div class="col-md-12 mb-2 text-end">
                <button type="submit" class="btn btn-success btn-sm">Save Profile</button>
              </div>
            </div>
          </form>
          <div v-else>
            <p><strong>Name:</strong> {{ profile.name }}
              &nbsp;|&nbsp; <strong>Branch:</strong> {{ profile.branch }}
              &nbsp;|&nbsp; <strong>CGPA:</strong> {{ profile.cgpa }}
              &nbsp;|&nbsp; <strong>Year:</strong> {{ profile.year }}
            </p>
          </div>
        </div>
      </div>

      <!-- Applications -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5><i class="bi bi-journal-text me-1"></i>My Applications</h5>
        <button class="btn btn-outline-secondary btn-sm" @click="exportCSV" :disabled="exporting">
          <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
          <i class="bi bi-download me-1"></i>Export CSV
        </button>
      </div>

      <div v-if="applications.length === 0" class="text-muted">You haven't applied to any drives yet.</div>
      <table v-else class="table table-bordered table-hover">
        <thead class="table-light">
          <tr>
            <th>#</th><th>Drive</th><th>Company</th><th>Status</th><th>Interview Details</th><th>Applied</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in applications" :key="a.id">
            <td>{{ a.id }}</td>
            <td>{{ a.drive_title }}</td>
            <td>{{ a.company_name }}</td>
            <td><span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span></td>
            <td>
              <div v-if="a.interview_date" class="small">
                <div><i class="bi bi-calendar-event me-1"></i>{{ formatDate(a.interview_date) }}</div>
                <div><i class="bi bi-camera-video me-1"></i>{{ a.interview_mode || '—' }}</div>
                <div v-if="a.interview_location"><i class="bi bi-geo-alt me-1"></i>{{ a.interview_location }}</div>
              </div>
              <span v-else class="text-muted small">—</span>
            </td>
            <td>{{ formatDate(a.applied_at) }}</td>
          </tr>
        </tbody>
      </table>
    </template>

    <!-- COMPANY DASHBOARD-->
    <template v-if="role === 'company'">
      <h2 class="mb-4"><i class="bi bi-building me-2"></i>Company Dashboard</h2>

      <!-- Profile card -->
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-info text-white">
          <i class="bi bi-briefcase me-1"></i> Company Profile
          <span class="badge bg-light text-dark ms-2">{{ profile.approval_status }}</span>
          <button class="btn btn-sm btn-light float-end" @click="editingProfile = !editingProfile">
            {{ editingProfile ? 'Cancel' : 'Edit' }}
          </button>
        </div>
        <div class="card-body">
          <form v-if="editingProfile" @submit.prevent="updateCompanyProfile">
            <div class="row">
              <div class="col-md-4 mb-2">
                <label class="form-label">Company Name</label>
                <input v-model="profile.company_name" class="form-control" required>
              </div>
              <div class="col-md-3 mb-2">
                <label class="form-label">HR Contact</label>
                <input v-model="profile.hr_contact" class="form-control" required>
              </div>
              <div class="col-md-3 mb-2">
                <label class="form-label">Website</label>
                <input v-model="profile.website" class="form-control" required>
              </div>
              <div class="col-md-2 mb-2 d-flex align-items-end">
                <button type="submit" class="btn btn-success btn-sm">Save</button>
              </div>
            </div>
            <div class="mb-2">
              <label class="form-label">Description</label>
              <textarea v-model="profile.description" class="form-control" rows="2" required></textarea>
            </div>
          </form>
          <div v-else>
            <p><strong>{{ profile.company_name }}</strong>
              &nbsp;|&nbsp; HR: {{ profile.hr_contact }}
              &nbsp;|&nbsp; {{ profile.website }}
            </p>
            <p class="text-muted small">{{ profile.description }}</p>
          </div>
        </div>
      </div>

      <!-- Create Drive Form -->
      <div v-if="profile.approval_status === 'approved'" class="card shadow-sm mb-4">
        <div class="card-header bg-success text-white">
          <i class="bi bi-plus-circle me-1"></i> Create Placement Drive
        </div>
        <div class="card-body">
          <form @submit.prevent="createDrive">
            <div class="row">
              <div class="col-md-6 mb-2">
                <label class="form-label">Job Title</label>
                <input v-model="newDrive.job_title" class="form-control" required>
              </div>
              <div class="col-md-6 mb-2">
                <label class="form-label">Deadline</label>
                <input v-model="newDrive.deadline" type="datetime-local" class="form-control" required>
              </div>
            </div>
            <div class="mb-2">
              <label class="form-label">Description</label>
              <textarea v-model="newDrive.description" class="form-control" rows="2" required></textarea>
            </div>
            <div class="row">
              <div class="col-md-4 mb-2">
                <label class="form-label">Eligible Branches (comma-separated)</label>
                <input v-model="newDrive.eligibility_branch" class="form-control"
                       placeholder="CSE, ECE, ME or all" required>
              </div>
              <div class="col-md-4 mb-2">
                <label class="form-label">Min CGPA</label>
                <input v-model.number="newDrive.eligibility_cgpa" type="number"
                       step="0.1" class="form-control" required>
              </div>
              <div class="col-md-4 mb-2">
                <label class="form-label">Min Year</label>
                <input v-model.number="newDrive.eligibility_year" type="number"
                       class="form-control" required>
              </div>
            </div>
            <button type="submit" class="btn btn-success">Create Drive</button>
          </form>
        </div>
      </div>
      <div v-else class="alert alert-warning">
        Your company needs admin approval before you can create placement drives.
      </div>

      <!-- My Drives -->
      <h5 class="mb-3">My Drives</h5>
      <div v-if="companyDrives.length === 0" class="text-muted">No drives created yet.</div>
      <div v-else>
        <div class="accordion" id="drivesAccordion">
          <div v-for="(d, idx) in companyDrives" :key="d.id" class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button"
                      data-bs-toggle="collapse" :data-bs-target="'#drive' + d.id">
                {{ d.job_title }}
                <span class="badge ms-2" :class="driveBadge(d.status)">{{ d.status }}</span>
                <span class="badge bg-secondary ms-2">{{ d.application_count }} applicants</span>
              </button>
            </h2>
            <div :id="'drive' + d.id" class="accordion-collapse collapse"
                 data-bs-parent="#drivesAccordion">
              <div class="accordion-body">
                <p>{{ d.description }}</p>
                <p class="small text-muted">
                  Branch: {{ d.eligibility_branch || 'All' }} |
                  CGPA: {{ d.eligibility_cgpa || 'Any' }} |
                  Year: {{ d.eligibility_year ? d.eligibility_year + '+' : 'Any' }} |
                  Deadline: {{ formatDate(d.deadline) }}
                </p>

                <!-- Load applicants -->
                <button class="btn btn-sm btn-outline-primary mb-2"
                        @click="loadApplicants(d.id)">
                  View Applicants
                </button>

                <table v-if="applicants[d.id] && applicants[d.id].length > 0"
                       class="table table-sm table-bordered">
                  <thead class="table-light">
                    <tr>
                      <th>Student</th><th>Branch</th><th>CGPA</th><th>Resume</th><th>Status</th><th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="a in applicants[d.id]" :key="a.id">
                      <td>{{ a.student_name }}</td>
                      <td>{{ a.student_branch }}</td>
                      <td>{{ a.student_cgpa }}</td>
                      <td>
                        <a v-if="a.student_resume" :href="'http://localhost:5000/api/resume/' + a.student_resume"
                           target="_blank" class="btn btn-sm btn-outline-secondary">
                          <i class="bi bi-file-earmark-pdf"></i> View
                        </a>
                        <span v-else class="text-muted small">N/A</span>
                      </td>
                      <td>
                         <span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span>
                         <div v-if="a.interview_date" class="small text-muted mt-1">
                           <i class="bi bi-calendar-event"></i> {{ formatDate(a.interview_date) }}
                         </div>
                      </td>
                      <td>
                        <div class="input-group input-group-sm mb-1">
                           <select class="form-select" @change="updateAppStatus(a.id, $event.target.value)">
                              <option value="">Status...</option>
                              <option value="shortlisted">Shortlist</option>
                              <option value="selected">Select</option>
                              <option value="rejected">Reject</option>
                           </select>
                        </div>
                        <!-- Schedule Interview -->
                        <div v-if="a.status === 'shortlisted'" class="mt-1">
                          <small class="text-muted d-block mb-1">Schedule Interview:</small>
                          <!-- Step 1: Interview Mode -->
                          <div class="input-group input-group-sm mb-1">
                            <select class="form-select" @change="ensureInterviewData(a.id); interviewData[a.id].mode = $event.target.value">
                              <option value="">Select Mode...</option>
                              <option value="online">Online</option>
                              <option value="offline">Offline</option>
                            </select>
                          </div>
                          <!-- Step 2: Interview Date & Time -->
                          <div v-if="interviewData[a.id] && interviewData[a.id].mode" class="input-group input-group-sm mb-1">
                            <span class="input-group-text"><i class="bi bi-calendar-event"></i></span>
                            <input type="datetime-local" class="form-control" placeholder="Interview Date & Time"
                                   @change="interviewData[a.id].date = $event.target.value">
                          </div>
                          <!-- Step 3: Location (only for offline mode) -->
                          <div v-if="interviewData[a.id] && interviewData[a.id].mode === 'offline'" class="mb-1">
                            <input type="text" class="form-control form-control-sm"
                                   placeholder="Enter interview location / address"
                                   @input="interviewData[a.id].location = $event.target.value">
                          </div>
                          <!-- Submit -->
                          <button v-if="interviewData[a.id] && interviewData[a.id].mode"
                                  class="btn btn-sm btn-outline-primary w-100"
                                  @click="scheduleInterview(a.id)">
                            <i class="bi bi-check-circle me-1"></i>Schedule Interview
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-else-if="applicants[d.id] && applicants[d.id].length === 0"
                     class="text-muted small">No applicants yet.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

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
  name: 'UserPanel',
  data() {
    return {
      profile: {},
      editingProfile: false,
      applications: [],
      companyDrives: [],
      applicants: {},
      interviewData: {},
      newDrive: {
        job_title: '', description: '', eligibility_branch: '',
        eligibility_cgpa: 0, eligibility_year: 0, deadline: ''
      },
      exporting: false,
      feedback: '',
      feedbackOk: true,
      refreshTimer: null
    }
  },
  computed: {
    role() { return localStorage.getItem('role') || '' },
    headers() {
      return { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    }
  },
  methods: {
    // Student
    async loadStudentData() {
      try {
        const [pRes, aRes] = await Promise.all([
          axios.get(`${API}/student/profile`, { headers: this.headers }),
          axios.get(`${API}/student/applications`, { headers: this.headers })
        ])
        this.profile = pRes.data
        this.applications = aRes.data.applications || []
      } catch {}
    },
    async updateStudentProfile() {
      try {
        await axios.put(`${API}/student/profile`, this.profile, { headers: this.headers })
        this.editingProfile = false
        this.showFeedback('Profile updated', true)
      } catch (e) { this.showFeedback(e.response?.data?.msg || 'Error', false) }
    },
    async handleResumeUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      const formData = new FormData()
      formData.append('resume', file)
      
      try {
        await axios.post(`${API}/student/upload-resume`, formData, {
          headers: { ...this.headers, 'Content-Type': 'multipart/form-data' }
        })
        this.showFeedback('Resume uploaded successfully', true)
        this.loadStudentData()
      } catch (e) {
        this.showFeedback(e.response?.data?.msg || 'Upload failed', false)
      }
    },
    async exportCSV() {
      this.exporting = true
      try {
        const res = await axios.post(`${API}/student/export-csv`, {}, { headers: this.headers })
        this.showFeedback(res.data.msg || 'Export started! You will be alerted via email/console when done.', true)
      } catch (e) { this.showFeedback(e.response?.data?.msg || 'Export failed', false) }
      this.exporting = false
    },

    //  Company
    async loadCompanyData() {
      try {
        const [pRes, dRes] = await Promise.all([
          axios.get(`${API}/company/profile`, { headers: this.headers }),
          axios.get(`${API}/drives/my`, { headers: this.headers })
        ])
        this.profile = pRes.data
        this.companyDrives = dRes.data.drives || []
      } catch {}
    },
    async updateCompanyProfile() {
      try {
        await axios.put(`${API}/company/profile`, this.profile, { headers: this.headers })
        this.editingProfile = false
        this.showFeedback('Profile updated', true)
      } catch (e) { this.showFeedback(e.response?.data?.msg || 'Error', false) }
    },
    async createDrive() {
      try {
        await axios.post(`${API}/drives`, this.newDrive, { headers: this.headers })
        this.showFeedback('Drive created (pending approval)', true)
        this.newDrive = { job_title: '', description: '', eligibility_branch: '',
                          eligibility_cgpa: 0, eligibility_year: 0, deadline: '' }
        this.loadCompanyData()
      } catch (e) { this.showFeedback(e.response?.data?.msg || 'Error', false) }
    },
    async loadApplicants(driveId) {
      try {
        const res = await axios.get(`${API}/company/applicants/${driveId}`,
                                    { headers: this.headers })
        this.applicants = { ...this.applicants, [driveId]: res.data.applicants || [] }
      } catch {}
    },
    async updateAppStatus(appId, status) {
      if (!status) return
      try {
        await axios.put(`${API}/company/application/${appId}`, { status },
                        { headers: this.headers })
        this.showFeedback(`Application ${status}`, true)

        for (const driveId of Object.keys(this.applicants)) {
          this.loadApplicants(parseInt(driveId))
        }
      } catch (e) { this.showFeedback(e.response?.data?.msg || 'Error', false) }
    },
    ensureInterviewData(appId) {
      if (!this.interviewData[appId]) {
        this.interviewData[appId] = { mode: '', location: '', date: '' }
      }
    },
    async scheduleInterview(appId) {
      const data = this.interviewData[appId] || {}
      if (!data.date || !data.mode) {
        this.showFeedback('Select mode and date for interview', false)
        return
      }
      try {
        await axios.post(`${API}/company/schedule-interview/${appId}`, {
          interview_date: data.date,
          interview_mode: data.mode,
          interview_location: data.location || ''
        }, { headers: this.headers })
        this.showFeedback('Interview scheduled', true)
        for (const driveId of Object.keys(this.applicants)) {
          this.loadApplicants(parseInt(driveId))
        }
      } catch (e) { this.showFeedback(e.response?.data?.msg || 'Error', false) }
    },

    // Helpers
    showFeedback(msg, ok) {
      this.feedback = msg
      this.feedbackOk = ok
      setTimeout(() => { this.feedback = '' }, 3000)
    },
    statusBadge(s) {
      return {
        applied: 'bg-secondary', shortlisted: 'bg-info text-dark',
        interview_scheduled: 'bg-primary', selected: 'bg-success',
        rejected: 'bg-danger', cancelled: 'bg-dark'
      }[s] || 'bg-secondary'
    },
    driveBadge(s) {
      return {
        pending: 'bg-warning text-dark', approved: 'bg-success',
        rejected: 'bg-danger', closed: 'bg-secondary'
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
    if (this.role === 'student') {
      this.loadStudentData()
      this.refreshTimer = setInterval(() => { this.loadStudentData() }, 10000)
    } else if (this.role === 'company') {
      this.loadCompanyData()
      this.refreshTimer = setInterval(() => { this.loadCompanyData() }, 10000)
    }
  },
  beforeUnmount() {
    if (this.refreshTimer) clearInterval(this.refreshTimer)
  }
}
</script>