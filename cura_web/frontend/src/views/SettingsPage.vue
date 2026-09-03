<template>
  <div class="page-content">
    <div class="header"><h1>Settings</h1></div>

    <!-- Appearance -->
    <div class="glass p-6 mb-4">
      <h2 style="font-size:18px;font-weight:700;margin-bottom:16px;">Appearance</h2>
      <p class="text-secondary" style="font-size:13px;margin-bottom:14px;">Choose the theme used across the dashboard.</p>
      <div class="theme-options">
        <button class="theme-card" :class="{ selected: !theme.dark }" @click="theme.set(false)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
          <span>Light</span>
        </button>
        <button class="theme-card" :class="{ selected: theme.dark }" @click="theme.set(true)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
          <span>Dark</span>
        </button>
      </div>
    </div>

    <!-- ESP32 Scanner -->
    <div class="glass p-6">
      <h2 style="font-size:18px;font-weight:700;margin-bottom:16px;">ESP32 NFC Scanner</h2>
      <p class="text-secondary" style="font-size:13px;margin-bottom:16px;">
        Connect the ESP32-S3 (PN532) reader via USB to scan and program NFC cards from this browser.
      </p>

      <div v-if="!serial.supported" class="badge badge-red">Web Serial not supported in this browser.</div>

      <template v-else>
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
          <div style="flex:1;min-width:220px;">
            <label class="input-label">Port</label>
            <select v-model="selectedPort" class="input">
              <option value="">— No saved port —</option>
              <option v-for="(p, i) in ports" :key="i" :value="i">{{ p.label }}</option>
            </select>
          </div>
          <div style="display:flex;gap:8px;padding-top:16px;">
            <button class="btn btn-sm" @click="addDevice" :disabled="serial.connecting">
              {{ serial.connecting ? 'Connecting…' : '+ Add Device' }}
            </button>
            <button
              v-if="serial.connected"
              class="btn btn-sm btn-danger"
              @click="serial.disconnect()"
            >Disconnect</button>
            <button
              v-else
              class="btn btn-sm"
              :disabled="selectedPort === '' || serial.connecting"
              @click="connectSelected"
            >Connect</button>
          </div>
        </div>

        <div class="mt-4" style="display:flex;align-items:center;gap:8px;">
          <span class="badge" :class="serial.connected ? '' : 'badge-red'">
            {{ serial.connected ? '● Connected — ' + serial.portName : '○ Disconnected' }}
          </span>
          <span v-if="serial.error" class="badge badge-red">{{ serial.error }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '../stores/theme'
import { useSerialStore } from '../stores/serial'
import { useDialog } from '../composables/useDialog'

const theme = useThemeStore()
const serial = useSerialStore()
const dialog = useDialog()

const ports = ref([])
const selectedPort = ref('')

function refreshPorts() {
  ports.value = serial.savedPorts().map((p) => ({ port: p, label: serial.portLabel(p) }))
  if (selectedPort.value !== '' && !ports.value[selectedPort.value]) selectedPort.value = ''
}

onMounted(refreshPorts)

async function addDevice() {
  const opened = await serial.connect()
  if (opened) refreshPorts()
  else if (serial.error) dialog.alertMsg(serial.error, 'ESP32')
}

async function connectSelected() {
  const item = ports.value[selectedPort.value]
  if (!item) return
  const ok = await serial.connectTo(item.port)
  if (!ok && serial.error) dialog.alertMsg(serial.error, 'ESP32')
}
</script>

<style scoped>
.theme-options {
  display: flex;
  gap: 12px;
}
.theme-card {
  flex: 1;
  max-width: 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 18px;
  border-radius: 18px;
  border: 1.5px solid var(--border);
  background: var(--bg-card);
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s;
}
.theme-card svg { width: 28px; height: 28px; }
.theme-card:hover { border-color: var(--ios-blue); }
.theme-card.selected {
  border-color: var(--ios-blue);
  color: var(--ios-blue);
  background: rgba(0,122,255,0.1);
}
</style>