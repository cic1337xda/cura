<template>
  <div class="page-content">
    <div class="header"><h1>Payrolls</h1><button class="btn" @click="showModal = true">+ Generate Payroll</button></div>
    <div class="search-bar mb-4" style="display:flex;gap:8px;align-items:center;"><input v-model="search" placeholder="Search by Payroll # or employee..." style="flex:1;" /><ScanBar @scan="search = $event" /></div>
    <div class="glass" style="overflow-x: auto;">
      <table><thead><tr><th>Payroll #</th><th>Employee</th><th>Salary</th><th>Status</th><th>Date</th><th></th></tr></thead>
        <tbody><tr v-for="p in filtered" :key="p.id"><td><strong style="font-family:monospace;">{{ p.payroll_number }}</strong></td><td>{{ p.doctor_name }}</td><td>{{ p.salary }}</td><td><span class="badge" :class="p.status === 'Paid' ? '' : 'badge-red'">{{ p.status || 'Pending' }}</span></td><td>{{ new Date(p.generated_at).toLocaleDateString() }}</td>
        <td><button class="btn btn-sm btn-danger" @click="remove(p.id)">×</button></td></tr></tbody></table>
    </div>

    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false"><div class="modal"><h2>Generate Payroll</h2>
      <form @submit.prevent="create">
        <div class="grid2"><div><label class="input-label">Employee Name</label><input v-model="f.doctor_name" class="input" required /></div>
        <div><label class="input-label">Employee #</label><input v-model="f.doctor_number" class="input" /></div></div>
        <div class="grid2 mt-4"><div><label class="input-label">Email</label><input v-model="f.doctor_email" type="email" class="input" /></div>
        <div><label class="input-label">Salary</label><input v-model="f.salary" class="input" /></div></div>
        <div class="mt-4"><label class="input-label">Status</label><select v-model="f.status" class="input"><option>Pending</option><option>Paid</option></select></div>
        <div class="mt-4"><label class="input-label">Description</label><textarea v-model="f.description" class="input" rows="3"></textarea></div>
        <div class="flex-between mt-6"><button type="button" class="btn btn-outline" @click="showModal = false">Cancel</button><button type="submit" class="btn">Generate</button></div>
      </form></div></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'; import axios from 'axios'; import { useDialog } from '../composables/useDialog'
import ScanBar from '../components/ScanBar.vue'
const dialog = useDialog()
const list = ref([]), showModal = ref(false), search = ref(''), f = ref({ doctor_name:'', doctor_number:'', doctor_email:'', salary:'', status:'Pending', description:'' })
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return list.value
  return list.value.filter(p => (p.payroll_number||'').toLowerCase().includes(q) || (p.doctor_name||'').toLowerCase().includes(q))
})
onMounted(async () => { try { const { data } = await axios.get('/ops/payrolls'); list.value = data } catch(e){} })
async function create() { try { await axios.post('/ops/payrolls', f.value); showModal.value = false; f.value = { doctor_name:'', doctor_number:'', doctor_email:'', salary:'', status:'Pending', description:'' }; const { data } = await axios.get('/ops/payrolls'); list.value = data } catch(e){ dialog.alertMsg('Failed') } }
async function remove(id) { const ok = await dialog.confirm('Delete this payroll?'); if (!ok) return; await axios.delete(`/ops/payrolls/${id}`); const { data } = await axios.get('/ops/payrolls'); list.value = data }
</script>