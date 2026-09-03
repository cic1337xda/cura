<template>
  <div class="page-content">
    <div class="header"><h1>Pharmacy</h1>
      <div style="display: flex; gap: 8px;">
        <button class="btn btn-sm btn-outline" @click="tab = 'drugs'" :style="tab === 'drugs' ? 'background:var(--ios-blue);color:#fff' : ''">Drugs</button>
        <button class="btn btn-sm btn-outline" @click="tab = 'categories'" :style="tab === 'categories' ? 'background:var(--ios-blue);color:#fff' : ''">Categories</button>
        <button class="btn" @click="showDrugModal = true">+ Add Drug</button>
      </div>
    </div>

    <div class="search-bar mb-4" style="display:flex;gap:8px;align-items:center;"><input v-model="search" placeholder="Search..." style="flex:1;" /><ScanBar @scan="search = $event" /></div>

    <template v-if="tab === 'categories'">
      <div class="glass" style="overflow-x: auto;">
        <table><thead><tr><th>Name</th><th>Vendor</th><th>Description</th><th></th></tr></thead>
          <tbody><tr v-for="c in filteredCats" :key="c.id"><td><strong>{{ c.name }}</strong></td><td>{{ c.vendor }}</td><td>{{ c.description?.substring(0,80) }}</td>
          <td><button class="btn btn-sm btn-danger" @click="deleteCategory(c.id)">×</button></td></tr></tbody></table>
      </div>
      <button class="btn btn-sm mt-4" @click="showCatModal = true">+ Add Category</button>
    </template>

    <template v-if="tab === 'drugs'">
      <div class="glass" style="overflow-x: auto;">
        <table><thead><tr><th>Name</th><th>Barcode</th><th>Category</th><th>Qty</th><th>Vendor</th><th></th></tr></thead>
          <tbody><tr v-for="d in filteredDrugs" :key="d.id"><td><strong>{{ d.name }}</strong></td><td>{{ d.barcode }}</td><td>{{ d.category }}</td><td>{{ d.quantity }}</td><td>{{ d.vendor }}</td>
          <td><button class="btn btn-sm btn-danger" @click="deleteDrug(d.id)">×</button></td></tr></tbody></table>
      </div>
    </template>

    <div class="modal-overlay" v-if="showDrugModal" @click.self="showDrugModal = false"><div class="modal"><h2>Add Drug</h2>
      <form @submit.prevent="addDrug">
        <div><label class="input-label">Drug Name</label><input v-model="df.name" class="input" required /></div>
        <div class="grid2 mt-4"><div><label class="input-label">Barcode</label><input v-model="df.barcode" class="input" /></div>
        <div><label class="input-label">Quantity</label><input v-model="df.quantity" class="input" /></div></div>
        <div class="grid2 mt-4"><div><label class="input-label">Category</label><input v-model="df.category" class="input" /></div>
        <div><label class="input-label">Vendor</label><input v-model="df.vendor" class="input" /></div></div>
        <div class="mt-4"><label class="input-label">Description</label><textarea v-model="df.description" class="input" rows="3"></textarea></div>
        <div class="flex-between mt-6"><button type="button" class="btn btn-outline" @click="showDrugModal = false">Cancel</button><button type="submit" class="btn">Add Drug</button></div>
      </form></div></div>

    <div class="modal-overlay" v-if="showCatModal" @click.self="showCatModal = false"><div class="modal"><h2>Add Category</h2>
      <form @submit.prevent="addCategory">
        <div><label class="input-label">Category Name</label><input v-model="cf.name" class="input" required /></div>
        <div class="grid2 mt-4"><div><label class="input-label">Vendor</label><input v-model="cf.vendor" class="input" /></div></div>
        <div class="mt-4"><label class="input-label">Description</label><textarea v-model="cf.description" class="input" rows="3"></textarea></div>
        <div class="flex-between mt-6"><button type="button" class="btn btn-outline" @click="showCatModal = false">Cancel</button><button type="submit" class="btn">Add Category</button></div>
      </form></div></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'; import axios from 'axios'; import { useDialog } from '../composables/useDialog'
import ScanBar from '../components/ScanBar.vue'
const dialog = useDialog()
const tab = ref('drugs'), drugs = ref([]), categories = ref([]), search = ref('')
const showDrugModal = ref(false), showCatModal = ref(false)
const df = ref({ name:'', barcode:'', description:'', quantity:'', category:'', vendor:'' })
const cf = ref({ name:'', vendor:'', description:'' })

const filteredDrugs = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return drugs.value
  return drugs.value.filter(d => (d.name||'').toLowerCase().includes(q) || (d.barcode||'').toLowerCase().includes(q) || (d.category||'').toLowerCase().includes(q) || (d.vendor||'').toLowerCase().includes(q))
})
const filteredCats = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return categories.value
  return categories.value.filter(c => (c.name||'').toLowerCase().includes(q) || (c.vendor||'').toLowerCase().includes(q))
})

async function fetchDrugs() { try { const { data } = await axios.get('/pharmacy/drugs'); drugs.value = data } catch(e){} }
async function fetchCats() { try { const { data } = await axios.get('/pharmacy/categories'); categories.value = data } catch(e){} }
onMounted(() => { fetchDrugs(); fetchCats() })

async function addDrug() { try { await axios.post('/pharmacy/drugs', df.value); showDrugModal.value = false; df.value = { name:'', barcode:'', description:'', quantity:'', category:'', vendor:'' }; await fetchDrugs() } catch(e){ dialog.alertMsg('Failed') } }
async function addCategory() { try { await axios.post('/pharmacy/categories', cf.value); showCatModal.value = false; cf.value = { name:'', vendor:'', description:'' }; await fetchCats() } catch(e){ dialog.alertMsg('Failed') } }
async function deleteDrug(id) { const ok = await dialog.confirm('Delete this drug?'); if (!ok) return; await axios.delete(`/pharmacy/drugs/${id}`); await fetchDrugs() }
async function deleteCategory(id) { const ok = await dialog.confirm('Delete this category?'); if (!ok) return; await axios.delete(`/pharmacy/categories/${id}`); await fetchCats() }
</script>