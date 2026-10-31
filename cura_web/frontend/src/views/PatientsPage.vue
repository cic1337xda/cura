<template>
  <div class="page-content">
    <div class="header"><h1>Patients</h1><button class="btn" @click="openAddModal">+ Register Patient</button></div>

    <div class="search-bar mb-4" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
      <input v-model="search" @input="fetchPatients" placeholder="Search by patient number or name..." style="flex:1;min-width:200px;" />
      <ScanBar @scan="onScanned" />
    </div>

    <div class="glass" style="overflow-x: auto;" v-if="!loading">
      <table>
        <thead><tr><th style="width:60px;"></th><th>Name</th><th>Number</th><th>IC / Card UID</th><th>Type</th><th>Age</th><th>Ailment</th><th>Status</th><th></th></tr></thead>
        <tbody><tr v-for="p in patients" :key="p.id">
          <td><div v-if="p.photo" style="width:36px;height:36px;border-radius:10px;overflow:hidden;"><img :src="p.photo" :alt="p.first_name + ' ' + p.last_name + ' Patient Photo'" style="width:100%;height:100%;object-fit:cover;" /></div>
          <div v-else style="width:36px;height:36px;border-radius:10px;background:var(--bg-card-hover);display:flex;align-items:center;justify-content:center;font-size:16px;">👤</div></td>
          <td><strong>{{ p.first_name }} {{ p.last_name }}</strong></td>
          <td style="font-family:monospace;">{{ p.patient_number }}</td>
          <td>
            <div v-if="p.ic_number" style="font-size:13px;">{{ p.ic_number }}</div>
            <div v-if="p.ic_card_uid" style="font-size:11px;font-family:monospace;color:var(--ios-blue);">💳 {{ p.ic_card_uid }}</div>
            <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">
              {{ p.nationality === 'Non-Malaysian' ? '🌐 Non-M\'sian' : '🇲🇾 M\'sian' }}
            </div>
            <div v-if="!p.ic_number && !p.ic_card_uid" class="text-secondary">—</div>
          </td>
          <td><span class="badge" :class="p.patient_type==='InPatient'?'badge-blue':''">{{ p.patient_type }}</span></td>
          <td>{{ p.age }}</td>
          <td>{{ p.ailment || '—' }}</td>
          <td><span v-if="p.discharge_status" class="badge badge-red">Discharged</span><span v-else class="badge">Active</span></td>
          <td>
            <button class="btn btn-sm" @click="viewPatient(p)" style="margin-right:4px;">View</button>
            <button class="btn btn-sm btn-outline" @click="openEditModal(p)" style="margin-right:4px;">Edit</button>
            <button class="btn btn-sm btn-danger" @click="deletePatient(p.id)">×</button>
          </td>
        </tr></tbody>
      </table>
    </div>

    <div class="modal-overlay" v-if="showModal" @click.self="closeModal"><div class="modal">
      <h2>{{ editingId ? 'Edit Patient' : 'Register New Patient' }}</h2>
      <form @submit.prevent="savePatient">
        <div class="grid2">
          <div><label class="input-label">First Name</label><input v-model="form.first_name" class="input" required /></div>
          <div><label class="input-label">Last Name</label><input v-model="form.last_name" class="input" required /></div>
        </div>
        <div class="mt-4">
          <label class="input-label">User ID</label>
          <div style="display:flex;align-items:center;gap:0;">
            <span class="uid-prefix">C00A</span>
            <input v-model="uidNumber" class="input uid-input" :readonly="!!editingId" maxlength="4" inputmode="numeric" pattern="\d*" placeholder="0001" />
          </div>
          <p v-if="!editingId" class="text-secondary" style="font-size:12px;margin-top:6px;">Auto-filled with the next number. You can edit it (1 – 9999).</p>
        </div>
        <div class="grid2 mt-4">
          <div><label class="input-label">IC Number (NRIC)</label><input v-model="form.ic_number" class="input" placeholder="e.g. 010203-04-5678" /></div>
          <div>
            <label class="input-label">IC Card UID (MyKad Chip)</label>
            <div style="display:flex;gap:6px;">
              <input v-model="form.ic_card_uid" class="input" style="font-family:monospace;letter-spacing:1px;" placeholder="e.g. CF289949" />
              <button type="button" class="btn btn-sm btn-outline" style="flex-shrink:0;" :disabled="scanningIc" @click="scanIcCard">
                {{ scanningIc ? 'Tapping…' : '📡 Tap IC' }}
              </button>
            </div>
          </div>
        </div>
        <div class="grid2 mt-4">
          <div><label class="input-label">Phone</label><input v-model="form.phone" class="input" /></div>
          <div><label class="input-label">Ailment</label><input v-model="form.ailment" class="input" /></div>
        </div>
        <div class="grid2 mt-4">
          <div><label class="input-label">Date of Birth</label><input type="date" v-model="form.date_of_birth" class="input" @change="calcAge" /></div>
          <div><label class="input-label">Age</label><input v-model="form.age" class="input" readonly /></div>
        </div>
        <div class="grid2 mt-4">
          <div>
            <label class="input-label">Type</label>
            <select v-model="form.patient_type" class="input">
              <option>OutPatient</option>
              <option>InPatient</option>
            </select>
          </div>
          <div>
            <label class="input-label">Nationality</label>
            <select v-model="form.nationality" class="input">
              <option value="Malaysian">🇲🇾 Malaysian</option>
              <option value="Non-Malaysian">🌐 Non-Malaysian</option>
            </select>
          </div>
        </div>
        <div class="mt-4"><label class="input-label">Address</label><input v-model="form.address" class="input" /></div>
        <div class="flex-between mt-6">
          <button type="button" class="btn btn-outline" @click="closeModal">Cancel</button>
          <button type="submit" class="btn">{{ editingId ? 'Update' : 'Register' }}</button>
        </div>
      </form>
    </div></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useDialog } from '../composables/useDialog'
import { useDevice } from '../composables/useDevice'
import { useSerialStore } from '../stores/serial'
import ScanBar from '../components/ScanBar.vue'
import { ID_PREFIX, formatId, parseId } from '../config/prefixes'

const dialog = useDialog()
const device = useDevice()
const serial = useSerialStore()
const router = useRouter()
const loading = ref(true), patients = ref([]), search = ref(''), showModal = ref(false), editingId = ref(null)
const uidNumber = ref('')
const scanningIc = ref(false)
const form = ref({ first_name:'', last_name:'', date_of_birth:'', age:'', ic_number:'', ic_card_uid:'', nationality:'Malaysian', phone:'', address:'', patient_type:'OutPatient', ailment:'' })

async function fetchPatients() {
  try {
    const params = search.value ? `?search=${search.value}` : ''
    const { data } = await axios.get(`/patients${params}`)
    patients.value = data
  } catch(e) { console.error(e) } finally { loading.value = false }
}
onMounted(fetchPatients)

function calcAge() {
  if (!form.value.date_of_birth) { form.value.age = ''; return }
  const dob = new Date(form.value.date_of_birth)
  const today = new Date()
  let age = today.getFullYear() - dob.getFullYear()
  const m = today.getMonth() - dob.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--
  form.value.age = String(age)
}

function resetForm() {
  editingId.value = null
  uidNumber.value = ''
  scanningIc.value = false
  form.value = { first_name:'', last_name:'', date_of_birth:'', age:'', ic_number:'', ic_card_uid:'', nationality:'Malaysian', phone:'', address:'', patient_type:'OutPatient', ailment:'' }
}

async function fetchNextNumber() {
  try {
    const { data } = await axios.get('/patients/next-number')
    uidNumber.value = parseId(ID_PREFIX.patient, data.number)
  } catch(e) {}
}

async function scanIcCard() {
  if (scanningIc.value) return
  scanningIc.value = true

  // 1. Phone Web NFC
  if (device.canUsePhoneNfc.value) {
    try {
      const ndef = new NDEFReader()
      await ndef.scan()
      const handler = ({ serialNumber }) => {
        const uid = (serialNumber || '').replace(/:/g, '').toUpperCase()
        if (uid) form.value.ic_card_uid = uid
        scanningIc.value = false
      }
      ndef.addEventListener('reading', handler, { once: true })
      setTimeout(() => { scanningIc.value = false }, 10000)
      return
    } catch(e) {
      // fallback
    }
  }

  // 2. Desktop WebSerial / ESP32
  if (device.canUseEsp32.value) {
    if (!serial.connected) {
      const ok = await dialog.confirm('Connect ESP32 scanner to read IC card?', 'Connect ESP32', 'Connect')
      if (!ok) { scanningIc.value = false; return }
      const opened = await serial.connect()
      if (!opened) { scanningIc.value = false; return }
    }
    const uid = await serial.readOnce(8000)
    scanningIc.value = false
    if (uid) {
      form.value.ic_card_uid = uid
    } else {
      dialog.alertMsg('No IC card detected. Tap the IC card on the ESP32 reader.', 'Scan Timeout')
    }
  } else {
    scanningIc.value = false
  }
}

async function openAddModal() { resetForm(); showModal.value = true; await fetchNextNumber() }
function openEditModal(p) {
  editingId.value = p.id
  form.value = {
    first_name: p.first_name, last_name: p.last_name,
    date_of_birth: p.date_of_birth || '', age: p.age || '',
    ic_number: p.ic_number || '', ic_card_uid: p.ic_card_uid || '',
    nationality: p.nationality || 'Malaysian',
    phone: p.phone || '',
    address: p.address || '', patient_type: p.patient_type, ailment: p.ailment || ''
  }
  uidNumber.value = parseId(ID_PREFIX.patient, p.patient_number || '')
  showModal.value = true
}
function closeModal() { showModal.value = false; resetForm() }

async function savePatient() {
  try {
    let patient_number = undefined
    const n = parseInt(uidNumber.value, 10)
    if (!isNaN(n) && n > 0 && n <= 9999) {
      patient_number = formatId(ID_PREFIX.patient, n)
    }
    const payload = { ...form.value, patient_number }
    if (editingId.value) {
      await axios.put(`/patients/${editingId.value}`, payload)
    } else {
      await axios.post('/patients', payload)
    }
    closeModal(); loading.value = true; await fetchPatients()
  } catch(e) { dialog.alertMsg(e.response?.data?.detail || 'Failed') }
}

async function deletePatient(id) {
  const ok = await dialog.confirm('Delete this patient and all related records?', 'Delete Patient')
  if (!ok) return
  await axios.delete(`/patients/${id}`); loading.value = true; await fetchPatients()
}
function viewPatient(p) { router.push(`/patients/${p.id}`) }

function onScanned(uid) {
  search.value = (uid || '').trim()
  fetchPatients()
}
</script>

<style scoped>
.uid-prefix {
  padding: 14px 16px;
  background: var(--bg-card-hover);
  border: 1.5px solid rgba(0,0,0,0.08);
  border-right: none;
  border-radius: 16px 0 0 16px;
  font-family: monospace;
  font-weight: 700;
  color: var(--ios-blue);
  letter-spacing: 1px;
}
html.dark .uid-prefix { border-color: rgba(255,255,255,0.08); }
.uid-input {
  border-radius: 0 16px 16px 0;
  font-family: monospace;
  font-size: 16px;
  letter-spacing: 1px;
}
</style>