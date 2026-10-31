<template>
  <div class="page-content" v-if="patient">
    <div class="header">
      <button class="btn btn-sm btn-outline" @click="$router.push('/patients')">← Back</button>
    </div>

    <div class="glass p-6" style="max-width: 900px;">
      <div style="display: flex; gap: 24px; align-items: flex-start;">
        <div style="flex-shrink: 0;">
          <div v-if="patient.photo" style="width: 100px; height: 100px; border-radius: 24px; overflow: hidden;">
            <img :src="patient.photo" :alt="patient.first_name + ' ' + patient.last_name + ' Patient Photo'" style="width:100%;height:100%;object-fit:cover;" />
          </div>
          <div v-else style="width:100px;height:100px;border-radius:24px;background:var(--bg-card-hover);display:flex;align-items:center;justify-content:center;font-size:40px;">
            👤
          </div>
        </div>
        <div style="flex:1;">
          <div class="flex-between mb-4">
            <h1 style="font-size:24px;">{{ patient.first_name }} {{ patient.last_name }}</h1>
            <span class="badge" :class="patient.patient_type==='InPatient'?'badge-blue':''">{{ patient.patient_type }}</span>
          </div>
          <div class="grid2">
            <div><label class="input-label">Patient Number</label><p style="font-family:monospace;font-size:18px;font-weight:700;">{{ patient.patient_number }}</p></div>
            <div><label class="input-label">Age / DOB</label><p>{{ patient.age }} / {{ patient.date_of_birth }}</p></div>
            <div><label class="input-label">Phone</label><p>{{ patient.phone || '—' }}</p></div>
            <div><label class="input-label">IC Number (NRIC)</label><p>{{ patient.ic_number || '—' }}</p></div>
            <div><label class="input-label">IC Card UID (MyKad Chip)</label><p style="font-family:monospace;color:var(--ios-blue);font-weight:600;">{{ patient.ic_card_uid ? '💳 ' + patient.ic_card_uid : '—' }}</p></div>
            <div><label class="input-label">Nationality</label><p>{{ patient.nationality === 'Non-Malaysian' ? '🌐 Non-Malaysian' : '🇲🇾 Malaysian' }}</p></div>
            <div><label class="input-label">Address</label><p>{{ patient.address || '—' }}</p></div>
            <div><label class="input-label">Ailment</label><p>{{ patient.ailment || '—' }}</p></div>
            <div>
              <label class="input-label">Status</label>
              <p v-if="patient.discharge_status"><span class="badge badge-red">Discharged</span></p>
              <p v-else><span class="badge">Active</span></p>
            </div>
          </div>
          <div class="flex-between mt-4" style="gap:8px;">
            <button v-if="!patient.discharge_status" class="btn btn-sm btn-outline" @click="discharge">Discharge</button>
            <button v-else class="btn btn-sm" @click="readmit">Re-admit</button>
            <button class="btn btn-sm btn-outline" @click="$router.push('/patients')">Edit in List</button>
            <label class="btn btn-sm btn-outline" style="cursor:pointer;">
              {{ patient.photo ? 'Change Photo' : 'Upload Photo' }}
              <input type="file" accept="image/*" hidden @change="uploadPhoto" />
            </label>
            <NfcWriteButton :uid="patient.patient_number" label="Write Card" />
          </div>
        </div>
      </div>
    </div>

    <!-- Related Records Tabs -->
    <div class="mt-6" style="display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;">
      <button v-for="t in tabs" :key="t.key" class="btn btn-sm"
        :class="tab === t.key ? '' : 'btn-outline'"
        @click="tab = t.key"
      >{{ t.label }}</button>
    </div>

    <div class="glass mt-4" style="overflow-x:auto;" v-if="!loading">
      <!-- Vitals -->
      <table v-if="tab==='vitals'"><thead><tr><th>Date</th><th>Temp</th><th>Pulse</th><th>Resp Rate</th><th>BP</th></tr></thead>
        <tbody><tr v-for="v in vitals" :key="v.id"><td>{{ new Date(v.recorded_at).toLocaleDateString() }}</td><td>{{ v.body_temp }}°C</td><td>{{ v.heart_pulse }}</td><td>{{ v.respiration_rate }}</td><td>{{ v.blood_pressure }}</td></tr>
        <tr v-if="vitals.length===0"><td colspan="5" class="text-center text-secondary">No vitals recorded.</td></tr></tbody></table>

      <!-- Prescriptions -->
      <table v-if="tab==='prescriptions'"><thead><tr><th>Rx #</th><th>Date</th><th>Ailment</th><th>Instructions</th></tr></thead>
        <tbody><tr v-for="r in prescriptions" :key="r.id"><td><strong>{{ r.prescription_number }}</strong></td><td>{{ new Date(r.created_at).toLocaleDateString() }}</td><td>{{ r.ailment }}</td><td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{{ r.instructions?.replace(/<[^>]*>/g,'') }}</td></tr>
        <tr v-if="prescriptions.length===0"><td colspan="4" class="text-center text-secondary">No prescriptions.</td></tr></tbody></table>

      <!-- Lab -->
      <table v-if="tab==='lab'"><thead><tr><th>Lab #</th><th>Date</th><th>Tests</th><th>Results</th></tr></thead>
        <tbody><tr v-for="l in lab" :key="l.id"><td><strong>{{ l.lab_number }}</strong></td><td>{{ new Date(l.recorded_at).toLocaleDateString() }}</td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{{ l.tests?.replace(/<[^>]*>/g,'') }}</td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{{ l.results?.replace(/<[^>]*>/g,'') }}</td></tr>
        <tr v-if="lab.length===0"><td colspan="4" class="text-center text-secondary">No lab records.</td></tr></tbody></table>

      <!-- Surgeries -->
      <table v-if="tab==='surgeries'"><thead><tr><th>Surg #</th><th>Date</th><th>Doctor</th><th>Status</th></tr></thead>
        <tbody><tr v-for="s in surgeries" :key="s.id"><td><strong>{{ s.surgery_number }}</strong></td><td>{{ new Date(s.date).toLocaleDateString() }}</td><td>{{ s.doctor }}</td><td><span class="badge" :class="s.status==='Successful'?'':'badge-red'">{{ s.status }}</span></td></tr>
        <tr v-if="surgeries.length===0"><td colspan="4" class="text-center text-secondary">No surgeries.</td></tr></tbody></table>

      <!-- Medical Records -->
      <table v-if="tab==='med'"><thead><tr><th>Rec #</th><th>Date</th><th>Ailment</th><th>Prescription</th></tr></thead>
        <tbody><tr v-for="r in medRecords" :key="r.id"><td><strong>{{ r.record_number }}</strong></td><td>{{ new Date(r.recorded_at).toLocaleDateString() }}</td><td>{{ r.ailment }}</td><td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{{ r.prescription?.replace(/<[^>]*>/g,'') }}</td></tr>
        <tr v-if="medRecords.length===0"><td colspan="4" class="text-center text-secondary">No medical records.</td></tr></tbody></table>
    </div>
  </div>
  <div v-else class="page-content"><p class="text-secondary">Loading...</p></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useDialog } from '../composables/useDialog'
import NfcWriteButton from '../components/NfcWriteButton.vue'
const dialog = useDialog()
const route = useRoute()
const patient = ref(null), loading = ref(true), tab = ref('vitals')
const vitals = ref([]), prescriptions = ref([]), lab = ref([]), surgeries = ref([]), medRecords = ref([])
const tabs = [
  { key: 'vitals', label: '💓 Vitals' },
  { key: 'prescriptions', label: '📝 Prescriptions' },
  { key: 'lab', label: '🔬 Lab' },
  { key: 'surgeries', label: '🏥 Surgeries' },
  { key: 'med', label: '📋 Med Records' },
]

onMounted(async () => {
  try {
    const id = route.params.id
    patient.value = (await axios.get(`/patients/${id}`)).data
    const [v, rx, l, s, d] = await Promise.all([
      axios.get(`/patients/${id}/vitals`),
      axios.get(`/patients/${id}/prescriptions`),
      axios.get(`/patients/${id}/lab-tests`),
      axios.get(`/patients/${id}/surgeries`),
      axios.get(`/patients/${id}/medical-records`),
    ])
    vitals.value = v.data; prescriptions.value = rx.data; lab.value = l.data; surgeries.value = s.data; medRecords.value = d.data
  } catch(e) { console.error(e) } finally { loading.value = false }
})

async function discharge() {
  const ok = await dialog.confirm('Discharge this patient?', 'Discharge', 'Confirm')
  if (!ok) return
  await axios.put(`/patients/${route.params.id}/discharge?status_text=Discharged`)
  patient.value = (await axios.get(`/patients/${route.params.id}`)).data
}
async function readmit() {
  const ok = await dialog.confirm('Re-admit this patient? This clears the discharged status and keeps the same patient number and history.', 'Re-admit Patient', 'Confirm')
  if (!ok) return
  await axios.put(`/patients/${route.params.id}/readmit`)
  patient.value = (await axios.get(`/patients/${route.params.id}`)).data
}
async function uploadPhoto(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = async (ev) => {
    const ok = await dialog.previewImage(ev.target.result, 'Confirm Photo')
    if (!ok) return
    const fd = new FormData(); fd.append('file', file)
    await axios.post(`/patients/${route.params.id}/photo`, fd)
    patient.value = (await axios.get(`/patients/${route.params.id}`)).data
  }
  reader.readAsDataURL(file)
}
</script>