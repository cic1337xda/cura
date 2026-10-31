<template>
  <div class="page-content">
    <div class="header">
      <h1>Dashboard</h1>
      <button class="btn btn-sm btn-outline" @click="logout">Sign Out</button>
    </div>
    <div v-if="loading" class="text-secondary p-6">Loading...</div>
    <template v-else>
      <div class="grid4 mb-4">
        <div class="glass stat-card stat-card-clickable" @click="router.push('/patients')" title="View Patients">
          <div class="stat-value">{{ stats.total_patients }}</div>
          <div class="stat-label">Patients →</div>
        </div>
        <div class="glass stat-card stat-card-clickable" @click="router.push('/patients')" title="View InPatients">
          <div class="stat-value">{{ stats.total_inpatients }}</div>
          <div class="stat-label">InPatients →</div>
        </div>
        <div class="glass stat-card stat-card-clickable" @click="router.push('/patients')" title="View OutPatients">
          <div class="stat-value">{{ stats.total_outpatients }}</div>
          <div class="stat-label">OutPatients →</div>
        </div>
        <div class="glass stat-card stat-card-clickable" @click="router.push('/doctors')" title="View Doctors">
          <div class="stat-value">{{ stats.total_doctors }}</div>
          <div class="stat-label">Doctors →</div>
        </div>
      </div>
      <div class="grid4">
        <div class="glass stat-card stat-card-clickable" @click="router.push('/pharmacy')" title="View Pharmacy">
          <div class="stat-value">{{ stats.total_pharmaceuticals }}</div>
          <div class="stat-label">Drugs →</div>
        </div>
        <div class="glass stat-card stat-card-clickable" @click="router.push('/equipment')" title="View Equipment">
          <div class="stat-value">{{ stats.total_equipment }}</div>
          <div class="stat-label">Equipment →</div>
        </div>
        <div class="glass stat-card stat-card-clickable" @click="router.push('/vendors')" title="View Vendors">
          <div class="stat-value">{{ stats.total_vendors }}</div>
          <div class="stat-label">Vendors →</div>
        </div>
        <div class="glass stat-card stat-card-clickable" @click="router.push('/payrolls')" title="View Payrolls">
          <div class="stat-value">{{ stats.total_payrolls }}</div>
          <div class="stat-label">Payrolls →</div>
        </div>
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

<style scoped>
.stat-card-clickable {
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  user-select: none;
}
.stat-card-clickable:hover {
  transform: translateY(-5px) scale(1.02);
  border-color: var(--ios-blue);
  box-shadow: 0 12px 32px rgba(0, 122, 255, 0.18);
  background: var(--bg-card-hover);
}
.stat-card-clickable:active {
  transform: scale(0.98);
}
</style>