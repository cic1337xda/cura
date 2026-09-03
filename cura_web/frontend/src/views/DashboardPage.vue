<template>
  <div class="page-content">
    <div class="header">
      <h1>Dashboard</h1>
      <button class="btn btn-sm btn-outline" @click="logout">Sign Out</button>
    </div>
    <div v-if="loading" class="text-secondary p-6">Loading...</div>
    <template v-else>
      <div class="grid4 mb-4">
        <div class="glass stat-card"><div class="stat-value">{{ stats.total_patients }}</div><div class="stat-label">Patients</div></div>
        <div class="glass stat-card"><div class="stat-value">{{ stats.total_inpatients }}</div><div class="stat-label">InPatients</div></div>
        <div class="glass stat-card"><div class="stat-value">{{ stats.total_outpatients }}</div><div class="stat-label">OutPatients</div></div>
        <div class="glass stat-card"><div class="stat-value">{{ stats.total_doctors }}</div><div class="stat-label">Doctors</div></div>
      </div>
      <div class="grid4">
        <div class="glass stat-card"><div class="stat-value">{{ stats.total_pharmaceuticals }}</div><div class="stat-label">Drugs</div></div>
        <div class="glass stat-card"><div class="stat-value">{{ stats.total_equipment }}</div><div class="stat-label">Equipment</div></div>
        <div class="glass stat-card"><div class="stat-value">{{ stats.total_vendors }}</div><div class="stat-label">Vendors</div></div>
        <div class="glass stat-card"><div class="stat-value">{{ stats.total_payrolls }}</div><div class="stat-label">Payrolls</div></div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(true)
const stats = ref({ total_patients: 0, total_inpatients: 0, total_outpatients: 0, total_doctors: 0, total_pharmaceuticals: 0, total_equipment: 0, total_vendors: 0, total_payrolls: 0 })

onMounted(async () => {
  try {
    const { data } = await axios.get('/patients/stats/dashboard')
    stats.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

function logout() {
  localStorage.removeItem('cura_token')
  localStorage.removeItem('cura_role')
  router.push('/login')
}
</script>