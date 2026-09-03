<template>
  <div class="page-content">
    <div class="header"><h1>Vitals</h1><button class="btn" @click="showModal = true">+ Record Vitals</button></div>
    <div class="search-bar mb-4" style="display:flex;gap:8px;align-items:center;"><input v-model="search" placeholder="Search by Record # or patient #..." style="flex:1;" /><ScanBar @scan="search = $event" /></div>
    <div class="glass" style="overflow-x: auto;">
      <table><thead><tr><th>Record #</th><th>Patient #</th><th>Temp (°C)</th><th>Pulse</th><th>Resp Rate</th><th>BP</th><th></th></tr></thead>
        <tbody><tr v-for="v in filtered" :key="v.id"><td><strong>{{ v.vitals_number }}</strong></td><td>{{ v.patient_number }}</td><td>{{ v.body_temp }}</td><td>{{ v.heart_pulse }}</td><td>{{ v.respiration_rate }}</td><td>{{ v.blood_pressure }}</td>
        <td><button class="btn btn-sm btn-danger" @click="remove(v.id)">×</button></td></tr></tbody></table>
    </div>

    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false"><div class="modal"><h2>Record Vitals</h2>
      <form @submit.prevent="create">
        <div><label class="input-label">Search Patient</label>
          <div style="position:relative;">
            <input v-model="patientSearch" @input="searchPatients" class="input" placeholder="Type patient number..." />
            <div v-if="searchResults.length" style="position:absolute;top:100%;left:0;right:0;z-index:10;background:var(--bg-card);backdrop-filter:blur(20px);border:1px solid var(--border);border-radius:16px;max-height:200px;overflow-y:auto;margin-top:4px;">
              <div v-for="r in searchResults" :key="r.id" @click="selectPatient(r)" style="padding:10px 16px;cursor:pointer;font-size:14px;" class="sidebar-link">{{ r.patient_number }} — {{ r.first_name }} {{ r.last_name }}</div>
            </div>
          </div>
        </div>
        <div v-if="f.patient_number" class="mt-2"><span class="badge badge-blue">{{ f.patient_number }}</span></div>
        <div class="grid2 mt-4"><div><label class="input-label">Body Temp (°C)</label><input v-model="f.body_temp" class="input" /></div>
        <div><label class="input-label">Heart Pulse (bpm)</label><input v-model="f.heart_pulse" class="input" /></div></div>
        <div class="grid2 mt-4"><div><label class="input-label">Resp Rate (/min)</label><input v-model="f.respiration_rate" class="input" /></div>
        <div><label class="input-label">Blood Pressure</label><input v-model="f.blood_pressure" class="input" placeholder="120/80" /></div></div>
        <div class="flex-between mt-6"><button type="button" class="btn btn-outline" @click="closeModal">Cancel</button><button type="submit" class="btn">Save Vitals</button></div>
      </form></div></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'; import axios from 'axios'; import { useDialog } from '../composables/useDialog'
import ScanBar from '../components/ScanBar.vue'
const dialog = useDialog()
const list = ref([]), showModal = ref(false), search = ref(''), patientSearch = ref(''), searchResults = ref([]), f = ref({ patient_number:'', body_temp:'', heart_pulse:'', respiration_rate:'', blood_pressure:'' })
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return list.value
  return list.value.filter(v =>
    (v.vitals_number || '').toLowerCase().includes(q) ||
    (v.patient_number || '').toLowerCase().includes(q)
  )
})
let searchTimer = null
onMounted(async () => { try { const { data } = await axios.get('/lab/vitals'); list.value = data } catch(e){} })
async function searchPatients() {
  if (!patientSearch.value || patientSearch.value.length < 1) { searchResults.value = []; return }
  clearTimeout(searchTimer); searchTimer = setTimeout(async () => { try { const { data } = await axios.get(`/patients/search?q=${patientSearch.value}`); searchResults.value = data } catch(e) {} }, 200)
}
function selectPatient(p) { f.value.patient_number = p.patient_number; patientSearch.value = `${p.patient_number} — ${p.first_name} ${p.last_name}`; searchResults.value = [] }
function closeModal() { showModal.value = false; patientSearch.value = ''; searchResults.value = []; f.value = { patient_number:'', body_temp:'', heart_pulse:'', respiration_rate:'', blood_pressure:'' } }
async function create() { try { await axios.post('/lab/vitals', f.value); closeModal(); const { data } = await axios.get('/lab/vitals'); list.value = data } catch(e){ dialog.alertMsg('Failed') } }
async function remove(id) { const ok = await dialog.confirm('Delete this vitals record?'); if (!ok) return; await axios.delete(`/lab/vitals/${id}`); const { data } = await axios.get('/lab/vitals'); list.value = data }
</script>