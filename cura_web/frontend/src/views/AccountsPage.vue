<template>
  <div class="page-content">
    <div class="header"><h1>Accounts</h1><button class="btn" @click="showModal = true">+ New Account</button></div>
    <div class="search-bar mb-4" style="display:flex;gap:8px;align-items:center;"><input v-model="search" placeholder="Search by Acc # or name..." style="flex:1;" /><ScanBar @scan="search = $event" /></div>
    <div class="glass" style="overflow-x: auto;">
      <table><thead><tr><th>Acc #</th><th>Name</th><th>Type</th><th>Amount</th><th></th></tr></thead>
        <tbody><tr v-for="a in filtered" :key="a.id"><td style="font-family:monospace;">{{ a.account_number }}</td><td><strong>{{ a.name }}</strong></td><td><span class="badge" :class="a.account_type === 'Receivable Account' ? 'badge-blue' : ''">{{ a.account_type }}</span></td><td>{{ a.amount }}</td>
        <td><button class="btn btn-sm btn-danger" @click="remove(a.id)">×</button></td></tr></tbody></table>
    </div>

    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false"><div class="modal"><h2>New Account</h2>
      <form @submit.prevent="create">
        <div><label class="input-label">Account Name</label><input v-model="f.name" class="input" required /></div>
        <div class="grid2 mt-4"><div><label class="input-label">Type</label><select v-model="f.account_type" class="input"><option>Payable Account</option><option>Receivable Account</option></select></div>
        <div><label class="input-label">Amount</label><input v-model="f.amount" class="input" /></div></div>
        <div class="mt-4"><label class="input-label">Description</label><textarea v-model="f.description" class="input" rows="3"></textarea></div>
        <div class="flex-between mt-6"><button type="button" class="btn btn-outline" @click="showModal = false">Cancel</button><button type="submit" class="btn">Save</button></div>
      </form></div></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'; import axios from 'axios'; import { useDialog } from '../composables/useDialog'
import ScanBar from '../components/ScanBar.vue'
const dialog = useDialog()
const list = ref([]), showModal = ref(false), search = ref(''), f = ref({ name:'', description:'', account_type:'Payable Account', amount:'' })
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return list.value
  return list.value.filter(a => (a.account_number||'').toLowerCase().includes(q) || (a.name||'').toLowerCase().includes(q))
})
onMounted(async () => { try { const { data } = await axios.get('/ops/accounts'); list.value = data } catch(e){} })
async function create() { try { await axios.post('/ops/accounts', f.value); showModal.value = false; f.value = { name:'', description:'', account_type:'Payable Account', amount:'' }; const { data } = await axios.get('/ops/accounts'); list.value = data } catch(e){ dialog.alertMsg('Failed') } }
async function remove(id) { const ok = await dialog.confirm('Delete this account?'); if (!ok) return; await axios.delete(`/ops/accounts/${id}`); const { data } = await axios.get('/ops/accounts'); list.value = data }
</script>