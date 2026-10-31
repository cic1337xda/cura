<template>
  <div class="page-content">
    <div class="header"><h1>Doctors</h1><button class="btn" @click="openAddModal">+ Add Doctor</button></div>

    <div class="search-bar mb-4" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
      <input v-model="search" placeholder="Search by name, employee # or email..." style="flex:1;min-width:200px;" />
      <ScanBar @scan="onScanned" />
    </div>

    <div class="glass" style="overflow-x: auto;" v-if="!loading">
      <table>
        <thead><tr><th style="width:50px;"></th><th>Name</th><th>Employee #</th><th>IC / Card UID</th><th>Email</th><th>Department</th><th></th></tr></thead>
        <tbody>
          <tr v-for="d in filtered" :key="d.id">
            <td><div v-if="d.avatar" style="width:36px;height:36px;border-radius:10px;overflow:hidden;"><img :src="d.avatar" :alt="d.first_name + ' ' + d.last_name + ' Avatar'" style="width:100%;height:100%;object-fit:cover;" /></div>
            <div v-else style="width:36px;height:36px;border-radius:10px;background:var(--bg-card-hover);display:flex;align-items:center;justify-content:center;font-size:16px;">👨‍⚕️</div></td>
            <td><strong>{{ d.first_name }} {{ d.last_name }}</strong></td>
            <td style="font-family:monospace;">{{ d.employee_number }}</td>
            <td>
              <div v-if="d.ic_number" style="font-size:13px;">{{ d.ic_number }}</div>
              <div v-if="d.ic_card_uid" style="font-size:11px;font-family:monospace;color:var(--ios-blue);">💳 {{ d.ic_card_uid }}</div>
              <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">
                {{ d.nationality === 'Non-Malaysian' ? '🌐 Non-M\'sian' : '🇲🇾 M\'sian' }}
              </div>
              <div v-if="!d.ic_number && !d.ic_card_uid" class="text-secondary">—</div>
            </td>
            <td>{{ d.email }}</td><td>{{ d.department || '—' }}</td>
            <td>
              <button class="btn btn-sm" @click="viewDoctor(d)" style="margin-right:4px;">View</button>
              <button class="btn btn-sm btn-outline" @click="openEditModal(d)" style="margin-right:4px;">Edit</button>
              <button class="btn btn-sm btn-danger" @click="remove(d.id)">×</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
      <div class="modal"><h2>{{ editingId ? 'Edit Doctor' : 'Add Doctor' }}</h2>
        <form @submit.prevent="saveDoctor">
          <div class="grid2"><div><label class="input-label">First Name</label><input v-model="f.first_name" class="input" required /></div>
          <div><label class="input-label">Last Name</label><input v-model="f.last_name" class="input" required /></div></div>
          <div class="grid2 mt-4"><div><label class="input-label">Email</label><input v-model="f.email" type="email" class="input" required /></div></div>

          <div class="mt-4" v-if="editingId">
            <label class="input-label">Employee ID</label>
            <input :value="f.employee_number" class="input" readonly />
          </div>
          <div class="mt-4" v-else>
            <label class="input-label">Employee ID</label>
            <div style="display:flex;align-items:center;">
              <span class="uid-prefix">C01A</span>
              <input v-model="empNumber" class="input uid-input" maxlength="4" inputmode="numeric" pattern="\d*" placeholder="0001" />
            </div>
            <p class="text-secondary" style="font-size:12px;margin-top:6px;">Auto-filled with the next number. You can edit it (1 – 9999).</p>
          </div>

          <div class="grid2 mt-4">
            <div><label class="input-label">IC Number (NRIC)</label><input v-model="f.ic_number" class="input" placeholder="e.g. 010203-04-5678" /></div>
            <div>
              <label class="input-label">IC Card UID (MyKad Chip)</label>
              <div style="display:flex;gap:6px;">
                <input v-model="f.ic_card_uid" class="input" style="font-family:monospace;letter-spacing:1px;" placeholder="e.g. CF289949" />
                <button type="button" class="btn btn-sm btn-outline" style="flex-shrink:0;" :disabled="scanningIc" @click="scanIcCard">
                  {{ scanningIc ? 'Tapping…' : '📡 Tap IC' }}
                </button>
              </div>
            </div>
          </div>
          <div class="grid2 mt-4">
            <div><label class="input-label">Department</label><input v-model="f.department" class="input" /></div>
            <div>
              <label class="input-label">Nationality</label>
              <select v-model="f.nationality" class="input">
                <option value="Malaysian">🇲🇾 Malaysian</option>
                <option value="Non-Malaysian">🌐 Non-Malaysian</option>
              </select>
            </div>
          </div>
          <div class="mt-4">
            <label class="input-label">{{ editingId ? 'New Password (optional)' : 'Password' }}</label>
            <input v-model="f.password" type="password" class="input" :required="!editingId" :placeholder="editingId ? 'Leave blank to keep current' : ''" />
          </div>
          <div class="flex-between mt-6"><button type="button" class="btn btn-outline" @click="closeModal">Cancel</button><button type="submit" class="btn">{{ editingId ? 'Update' : 'Add' }}</button></div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
const loading = ref(true), doctors = ref([]), showModal = ref(false), search = ref('')
const empNumber = ref('')
const editingId = ref(null)
const scanningIc = ref(false)
const f = ref({ first_name:'', last_name:'', email:'', ic_number:'', ic_card_uid:'', nationality:'Malaysian', employee_number:'', department:'', password:'' })

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return doctors.value
  return doctors.value.filter(d =>
    `${d.first_name} ${d.last_name}`.toLowerCase().includes(q) ||
    (d.employee_number || '').toLowerCase().includes(q) ||
    (d.ic_card_uid || '').toLowerCase().includes(q) ||
    (d.ic_number || '').toLowerCase().includes(q) ||
    (d.nationality || '').toLowerCase().includes(q) ||
    (d.email || '').toLowerCase().includes(q)
  )
})

async function fetch() { try { const { data } = await axios.get('/doctors'); doctors.value = data } finally { loading.value = false } }
onMounted(fetch)

function viewDoctor(d) { router.push(`/doctors/${d.id}`) }

async function fetchNextNumber() {
  try { const { data } = await axios.get('/doctors/next-number'); empNumber.value = parseId(ID_PREFIX.doctor, data.number) } catch(e) {}
}

async function scanIcCard() {
  if (scanningIc.value) return
  scanningIc.value = true

  if (device.canUsePhoneNfc.value) {
    try {
      const ndef = new NDEFReader()
      await ndef.scan()
      const handler = ({ serialNumber }) => {
        const uid = (serialNumber || '').replace(/:/g, '').toUpperCase()
        if (uid) f.value.ic_card_uid = uid
        scanningIc.value = false
      }
      ndef.addEventListener('reading', handler, { once: true })
      setTimeout(() => { scanningIc.value = false }, 10000)
      return
    } catch(e) {}
  }

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
      f.value.ic_card_uid = uid
    } else {
      dialog.alertMsg('No IC card detected. Tap the IC card on the ESP32 reader.', 'Scan Timeout')
    }
  } else {
    scanningIc.value = false
  }
}

function openAddModal() {
  editingId.value = null
  scanningIc.value = false
  f.value = { first_name:'', last_name:'', email:'', ic_number:'', ic_card_uid:'', nationality:'Malaysian', employee_number:'', department:'', password:'' }
  empNumber.value = ''
  showModal.value = true
  fetchNextNumber()
}

function openEditModal(d) {
  editingId.value = d.id
  scanningIc.value = false
  f.value = {
    first_name: d.first_name, last_name: d.last_name,
    email: d.email, ic_number: d.ic_number || '', ic_card_uid: d.ic_card_uid || '',
    nationality: d.nationality || 'Malaysian',
    employee_number: d.employee_number, department: d.department || '',
    password: ''
  }
  empNumber.value = parseId(ID_PREFIX.doctor, d.employee_number || '')
  showModal.value = true
}

function closeModal() { showModal.value = false; editingId.value = null }

async function saveDoctor() {
  try {
    if (editingId.value) {
      const payload = { ...f.value, password: f.value.password || '' }
      await axios.put(`/doctors/${editingId.value}`, payload)
    } else {
      const n = parseInt(empNumber.value, 10)
      const employee_number = !isNaN(n) && n > 0 && n <= 9999 ? formatId(ID_PREFIX.doctor, n) : undefined
      await axios.post('/doctors', { ...f.value, employee_number })
    }
    closeModal()
    loading.value = true; await fetch()
  } catch(e) { dialog.alertMsg(e.response?.data?.detail || 'Failed') }
}

async function remove(id) { const ok = await dialog.confirm('Delete this doctor?'); if (!ok) return; await axios.delete(`/doctors/${id}`); loading.value = true; await fetch() }

function onScanned(uid) { search.value = (uid || '').trim() }
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
.uid-input { border-radius: 0 16px 16px 0; font-family: monospace; font-size: 16px; letter-spacing: 1px; }
</style>