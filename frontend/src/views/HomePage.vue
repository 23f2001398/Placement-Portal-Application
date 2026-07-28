<template>
  <div class="container">
    <div class="row justify-content-center align-items-center" style="min-height: 80vh;">
      <div class="col-md-6 text-center">
        <h1 class="display-4 fw-bold mb-5">Welcome to Placement Portal Application</h1>
        <div class="d-flex justify-content-center gap-3">
          <router-link to="/login" class="btn btn-primary btn-lg px-4">Login</router-link>
          <router-link to="/register" class="btn btn-outline-primary btn-lg px-4">Register</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage'
}
</script>