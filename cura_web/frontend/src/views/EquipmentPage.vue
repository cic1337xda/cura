<template>
  <div class="page-content">
    <div class="header"><h1>Equipment &amp; Assets</h1><button class="btn" @click="showModal = true">+ Add Equipment</button></div>
    <div class="search-bar mb-4" style="display:flex;gap:8px;align-items:center;"><input v-model="search" placeholder="Search by code or name..." style="flex:1;" /><ScanBar @scan="search = $event" /></div>
    <div class="glass" style="overflow-x: auto;">
      <table><thead><tr><th>Code</th><th>Name</th><th>Dept</th><th>Vendor</th><th>Status</th><th>Qty</th><th></th></tr></thead>
        <tbody><tr v-for="e in filtered" :key="e.id"><td>{{ e.code }}</td><td><strong>{{ e.name }}</strong></td><td>{{ e.department }}</td><td>{{ e.vendor }}</td><td><span class="badge" :class="e.status === 'Functioning' ? '' : 'badge-red'">{{ e.status }}</span></td><td>{{ e.quantity }}</td>
        <td><button class="btn btn-sm btn-danger" @click="remove(e.id)">×</button></td></tr></tbody></table>
    </div>

    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false"><div class="modal"><h2>Add Equipment</h2>
      <form @submit.prevent="create">
        <div class="grid2"><div><label class="input-label">Code</label><input v-model="f.code" class="input" /></div>
        <div><label class="input-label">Name</label><input v-model="f.name" class="input" required /></div></div>
        <div class="grid2 mt-4"><div><label class="input-label">Department</label><input v-model="f.department" class="input" /></div>
        <div><label class="input-label">Vendor</label><input v-model="f.vendor" class="input" /></div></div>
        <div class="grid2 mt-4"><div><label class="input-label">Status</label><select v-model="f.status" class="input"><option>Functioning</option><option>Under Repair</option></select></div>
        <div><label class="input-label">Quantity</label><input v-model="f.quantity" class="input" /></div></div>
        <div class="mt-4"><label class="input-label">Description</label><textarea v-model="f.description" class="input" rows="3"></textarea></div>
        <div class="flex-between mt-6"><button type="button" class="btn btn-outline" @click="showModal = false">Cancel</button><button type="submit" class="btn">Save</button></div>
      </form></div></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'; import axios from 'axios'; import { useDialog } from '../composables/useDialog'
import ScanBar from '../components/ScanBar.vue'
const dialog = useDialog()
const list = ref([]), showModal = ref(false), search = ref(''), f = ref({ code:'', name:'', vendor:'', description:'', department:'', status:'Functioning', quantity:'' })
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return list.value
  return list.value.filter(e => (e.code||'').toLowerCase().includes(q) || (e.name||'').toLowerCase().includes(q) || (e.department||'').toLowerCase().includes(q) || (e.vendor||'').toLowerCase().includes(q))
})
onMounted(async () => { try { const { data } = await axios.get('/ops/equipment'); list.value = data } catch(e){} })
async function create() { try { await axios.post('/ops/equipment', f.value); showModal.value = false; f.value = { code:'', name:'', vendor:'', description:'', department:'', status:'Functioning', quantity:'' }; const { data } = await axios.get('/ops/equipment'); list.value = data } catch(e){ dialog.alertMsg('Failed') } }
async function remove(id) { const ok = await dialog.confirm('Delete this equipment?'); if (!ok) return; await axios.delete(`/ops/equipment/${id}`); const { data } = await axios.get('/ops/equipment'); list.value = data }
</script>