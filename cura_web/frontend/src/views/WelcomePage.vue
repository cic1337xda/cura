<template>
  <div class="welcome">
    <div class="landing-container glass" style="z-index: 1; position: relative;">
      <h1><span>Cura.</span> HMS</h1>
      <p class="text-secondary" style="margin-top: 8px;">A premium Hospital Management Information System — streamlining patient care, pharmacy, laboratory, and operations with physical NFC integration.</p>
      <div class="actions" style="margin-top: 28px;">
        <router-link to="/login" class="btn">Admin Login</router-link>
        <router-link to="/login?role=doctor" class="btn btn-outline">Doctor Login</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>