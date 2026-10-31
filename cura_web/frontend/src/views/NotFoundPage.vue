<template>
  <div class="page-content" style="display: flex; align-items: center; justify-content: center; min-height: 80vh;">
    <div class="glass p-6 text-center" style="max-width: 480px; width: 100%;">
      <h1 style="font-size: 72px; font-weight: 900; letter-spacing: -2px; color: var(--ios-blue); margin-bottom: 8px;">404</h1>
      <h2 style="font-size: 22px; font-weight: 700; margin-bottom: 10px;">Page Not Found</h2>
      <p class="text-secondary" style="font-size: 14px; line-height: 1.5; margin-bottom: 24px;">
        The requested clinical file or terminal destination does not exist or has been relocated.
      </p>
      <div style="display: flex; gap: 12px; justify-content: center;">
        <router-link to="/" class="btn btn-outline">Home</router-link>
        <router-link to="/dashboard" class="btn">Dashboard</router-link>
      </div>
      <div class="mt-6 text-secondary" style="font-size: 12px;">
        © {{ currentYear }} Cura. HMS
      </div>
    </div>
  </div>
</template>

<script setup>
const currentYear = new Date().getFullYear()
</script>
