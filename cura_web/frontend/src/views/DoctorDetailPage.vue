<template>
  <div class="page-content" v-if="doc">
    <div class="header">
      <button class="btn btn-sm btn-outline" @click="$router.push('/doctors')">← Back</button>
    </div>

    <div class="glass p-6" style="max-width: 700px;">
      <div style="display: flex; gap: 24px; align-items: flex-start;">
        <div style="flex-shrink: 0;">
          <div v-if="doc.avatar" style="width: 100px; height: 100px; border-radius: 24px; overflow: hidden;">
            <img :src="doc.avatar" :alt="doc.first_name + ' ' + doc.last_name + ' Profile Photo'" style="width:100%;height:100%;object-fit:cover;" />
          </div>
          <div v-else style="width:100px;height:100px;border-radius:24px;background:var(--bg-card-hover);display:flex;align-items:center;justify-content:center;font-size:40px;">
            👨‍⚕️
          </div>
        </div>
        <div style="flex:1;">
          <h1 style="font-size:24px;">{{ doc.first_name }} {{ doc.last_name }}</h1>
          <div class="grid2 mt-4">
            <div><label class="input-label">Employee Number</label><p style="font-family:monospace;font-size:18px;font-weight:700;">{{ doc.employee_number }}</p></div>
            <div><label class="input-label">Email</label><p>{{ doc.email }}</p></div>
            <div><label class="input-label">Department</label><p>{{ doc.department || '—' }}</p></div>
            <div><label class="input-label">IC Number (NRIC)</label><p>{{ doc.ic_number || '—' }}</p></div>
            <div><label class="input-label">IC Card UID (MyKad Chip)</label><p style="font-family:monospace;color:var(--ios-blue);font-weight:600;">{{ doc.ic_card_uid ? '💳 ' + doc.ic_card_uid : '—' }}</p></div>
            <div><label class="input-label">Nationality</label><p>{{ doc.nationality === 'Non-Malaysian' ? '🌐 Non-Malaysian' : '🇲🇾 Malaysian' }}</p></div>
          </div>
          <div class="mt-4" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
            <label class="btn btn-sm btn-outline" style="cursor:pointer;">
              {{ doc.avatar ? 'Change Photo' : 'Upload Photo' }}
              <input type="file" accept="image/*" hidden @change="uploadPhoto" />
            </label>
            <NfcWriteButton :uid="doc.employee_number" label="Write Card" />
          </div>
        </div>
      </div>
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
const doc = ref(null)

onMounted(async () => {
  try { const { data } = await axios.get(`/doctors/${route.params.id}`); doc.value = data } catch(e) { console.error(e) }
})

async function uploadPhoto(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = async (ev) => {
    const ok = await dialog.previewImage(ev.target.result, 'Confirm Photo')
    if (!ok) return
    const fd = new FormData(); fd.append('file', file)
    await axios.post(`/doctors/${route.params.id}/photo`, fd)
    const { data } = await axios.get(`/doctors/${route.params.id}`); doc.value = data
  }
  reader.readAsDataURL(file)
}
</script>