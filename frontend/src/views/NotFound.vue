<template>
  <div class="container">
    <div class="row justify-content-center align-items-center" style="min-height: 60vh;">
      <div class="col-md-6 text-center">
        <h1 class="display-1 fw-bold text-primary">404</h1>
        <h3 class="mb-3">Page Not Found</h3>
        <p class="text-muted mb-4">The page you are looking for does not exist.</p>
        <router-link to="/" class="btn btn-primary">Go to Home</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>