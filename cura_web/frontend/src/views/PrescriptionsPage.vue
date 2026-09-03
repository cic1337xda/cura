<template>
  <div class="page-content">
    <div class="header"><h1>Prescriptions</h1><button class="btn" @click="showModal = true">+ New Prescription</button></div>
    <div class="search-bar mb-4" style="display:flex;gap:8px;align-items:center;"><input v-model="search" placeholder="Search by Rx # or patient..." style="flex:1;" /><ScanBar @scan="search = $event" /></div>
    <div class="glass" style="overflow-x: auto;">
      <table><thead><tr><th>Rx #</th><th>Patient</th><th>Patient #</th><th>Age</th><th>Ailment</th><th>Date</th><th></th></tr></thead>
        <tbody><tr v-for="r in filtered" :key="r.id"><td><strong>{{ r.prescription_number }}</strong></td><td>{{ r.patient_name }}</td><td>{{ r.patient_number }}</td><td>{{ r.patient_age }}</td><td>{{ r.ailment }}</td><td>{{ new Date(r.created_at).toLocaleDateString() }}</td>
        <td><button class="btn btn-sm btn-danger" @click="remove(r.id)">×</button></td></tr></tbody></table>
    </div>

    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false"><div class="modal"><h2>New Prescription</h2>
      <form @submit.prevent="create">
        <div><label class="input-label">Search Patient</label>
          <div style="position:relative;">
            <input v-model="patientSearch" @input="searchPatients" class="input" placeholder="Type patient number..." />
            <div v-if="searchResults.length" style="position:absolute;top:100%;left:0;right:0;z-index:10;background:var(--bg-card);backdrop-filter:blur(20px);border:1px solid var(--border);border-radius:16px;max-height:200px;overflow-y:auto;margin-top:4px;">
              <div v-for="r in searchResults" :key="r.id" @click="selectPatient(r)" style="padding:10px 16px;cursor:pointer;font-size:14px;" class="sidebar-link">{{ r.patient_number }} — {{ r.first_name }} {{ r.last_name }}</div>
            </div>
          </div>
        </div>
        <div v-if="f.patient_number" class="mt-2"><span class="badge badge-blue">{{ f.patient_name }} ({{ f.patient_number }})</span></div>
        <div class="mt-4"><label class="input-label">Ailment / Diagnosis</label><input v-model="f.ailment" class="input" /></div>
        <div class="mt-4"><label class="input-label">Prescription Instructions</label><textarea v-model="f.instructions" class="input" rows="4"></textarea></div>
        <div class="flex-between mt-6"><button type="button" class="btn btn-outline" @click="closeModal">Cancel</button><button type="submit" class="btn">Issue Prescription</button></div>
      </form></div></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'; import axios from 'axios'; import { useDialog } from '../composables/useDialog'
import ScanBar from '../components/ScanBar.vue'
const dialog = useDialog()
const list = ref([]), showModal = ref(false), search = ref(''), patientSearch = ref(''), searchResults = ref([])
const f = ref({ patient_name:'', patient_age:'', patient_number:'', patient_address:'', patient_type:'InPatient', ailment:'', instructions:'' })
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return list.value
  return list.value.filter(r =>
    (r.prescription_number || '').toLowerCase().includes(q) ||
    (r.patient_name || '').toLowerCase().includes(q) ||
    (r.patient_number || '').toLowerCase().includes(q)
  )
})
let searchTimer = null
onMounted(async () => { try { const { data } = await axios.get('/pharmacy/prescriptions'); list.value = data } catch(e){} })
async function searchPatients() {
  if (!patientSearch.value || patientSearch.value.length < 1) { searchResults.value = []; return }
  clearTimeout(searchTimer); searchTimer = setTimeout(async () => { try { const { data } = await axios.get(`/patients/search?q=${patientSearch.value}`); searchResults.value = data } catch(e) {} }, 200)
}
function selectPatient(p) { f.value.patient_name = `${p.first_name} ${p.last_name}`; f.value.patient_number = p.patient_number; f.value.patient_age = p.age; f.value.patient_address = p.address; f.value.patient_type = p.patient_type; patientSearch.value = `${p.patient_number} — ${p.first_name} ${p.last_name}`; searchResults.value = [] }
function closeModal() { showModal.value = false; patientSearch.value = ''; searchResults.value = []; f.value = { patient_name:'', patient_age:'', patient_number:'', patient_address:'', patient_type:'InPatient', ailment:'', instructions:'' } }
async function create() { try { await axios.post('/pharmacy/prescriptions', f.value); closeModal(); const { data } = await axios.get('/pharmacy/prescriptions'); list.value = data } catch(e){ dialog.alertMsg('Failed') } }
async function remove(id) { const ok = await dialog.confirm('Delete this prescription?'); if (!ok) return; await axios.delete(`/pharmacy/prescriptions/${id}`); const { data } = await axios.get('/pharmacy/prescriptions'); list.value = data }
</script>