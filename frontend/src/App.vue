<template>
  <div id="ppa-app">
    <!--Navbar-->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
      <div class="container">
        <router-link class="navbar-brand fw-bold" to="/">
          Placement Portal
        </router-link>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">

            <!-- If not logged in -->
            <template v-if="!isLoggedIn">
              <li class="nav-item">
                <router-link class="nav-link" to="/login">Login</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/register">Register</router-link>
              </li>
            </template>

            <!-- If logged in-->
            <template v-else>
              <li class="nav-item" v-if="role === 'admin'">
                <router-link class="nav-link" to="/admin">Dashboard</router-link>
              </li>
              <li class="nav-item" v-if="role === 'admin'">
                <router-link class="nav-link" to="/admin/summary">Summary</router-link>
              </li>
              <li class="nav-item" v-if="role === 'company' || role === 'student'">
                <router-link class="nav-link" to="/dashboard">Dashboard</router-link>
              </li>
              <li class="nav-item" v-if="role === 'student'">
                <router-link class="nav-link" to="/user/summary">My Summary</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/drives">Drives</router-link>
              </li>
              <li class="nav-item">
                <a class="nav-link text-warning" href="#" @click.prevent="logout">
                  <i class="bi bi-box-arrow-right me-1"></i>Logout
                </a>
              </li>
            </template>
          </ul>
        </div>
      </div>
    </nav>

    <!--Content-->
    <main class="container py-4">
      <router-view />
    </main>


  </div>
</template>

<script>
import auth, { logout } from './store'

export default {
  name: 'App',
  computed: {
    isLoggedIn() { return !!auth.token },
    role() { return auth.role }
  },
  methods: {
    logout() {
      logout()
      this.$router.push('/login')
    }
  }
}
</script>

<style>

#ppa-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
main {
  flex: 1;
}
</style>