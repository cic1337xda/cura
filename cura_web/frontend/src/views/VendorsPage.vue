<template>
  <div class="page-content">
    <div class="header"><h1>Vendors</h1><button class="btn" @click="showModal = true">+ Add Vendor</button></div>
    <div class="search-bar mb-4" style="display:flex;gap:8px;align-items:center;"><input v-model="search" placeholder="Search by vendor # or name..." style="flex:1;" /><ScanBar @scan="search = $event" /></div>
    <div class="glass" style="overflow-x: auto;">
      <table><thead><tr><th>Vendor #</th><th>Name</th><th>Email</th><th>Phone</th><th></th></tr></thead>
        <tbody><tr v-for="v in filtered" :key="v.id"><td style="font-family:monospace;">{{ v.vendor_number }}</td><td><strong>{{ v.name }}</strong></td><td>{{ v.email }}</td><td>{{ v.phone || v.mobile }}</td>
        <td><button class="btn btn-sm btn-danger" @click="remove(v.id)">×</button></td></tr></tbody></table>
    </div>

    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false"><div class="modal"><h2>Add Vendor</h2>
      <form @submit.prevent="create">
        <div><label class="input-label">Vendor Name</label><input v-model="f.name" class="input" required /></div>
        <div class="grid2 mt-4"><div><label class="input-label">Email</label><input v-model="f.email" type="email" class="input" /></div>
        <div><label class="input-label">Mobile</label><input v-model="f.mobile" class="input" /></div></div>
        <div class="grid2 mt-4"><div><label class="input-label">Phone</label><input v-model="f.phone" class="input" /></div>
        <div><label class="input-label">Address</label><input v-model="f.address" class="input" /></div></div>
        <div class="mt-4"><label class="input-label">Description</label><textarea v-model="f.description" class="input" rows="3"></textarea></div>
        <div class="flex-between mt-6"><button type="button" class="btn btn-outline" @click="showModal = false">Cancel</button><button type="submit" class="btn">Save</button></div>
      </form></div></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'; import axios from 'axios'; import { useDialog } from '../composables/useDialog'
import ScanBar from '../components/ScanBar.vue'
const dialog = useDialog()
const list = ref([]), showModal = ref(false), search = ref(''), f = ref({ name:'', address:'', mobile:'', email:'', phone:'', description:'' })
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return list.value
  return list.value.filter(v => (v.vendor_number||'').toLowerCase().includes(q) || (v.name||'').toLowerCase().includes(q) || (v.email||'').toLowerCase().includes(q))
})
onMounted(async () => { try { const { data } = await axios.get('/ops/vendors'); list.value = data } catch(e){} })
async function create() { try { await axios.post('/ops/vendors', f.value); showModal.value = false; f.value = { name:'', address:'', mobile:'', email:'', phone:'', description:'' }; const { data } = await axios.get('/ops/vendors'); list.value = data } catch(e){ dialog.alertMsg('Failed') } }
async function remove(id) { const ok = await dialog.confirm('Delete this vendor?'); if (!ok) return; await axios.delete(`/ops/vendors/${id}`); const { data } = await axios.get('/ops/vendors'); list.value = data }
</script>