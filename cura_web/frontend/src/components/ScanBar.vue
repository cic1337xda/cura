<template>
  <div class="scanbar">
    <button
      type="button"
      class="scan-btn"
      :class="{ active: phoneScanning }"
      :disabled="!device.canUsePhoneNfc.value"
      :title="phoneTitle"
      @click="phoneScan"
    >
      <svg class="scan-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <rect x="6" y="2.5" width="12" height="19" rx="2.5" />
        <line x1="10" y1="18.5" x2="14" y2="18.5" />
        <path d="M6.5 7.5a5 5 0 0 0 0 7" />
        <path d="M4.5 5.5a8 8 0 0 0 0 11" />
      </svg>
      <span>{{ phoneScanning ? 'Scanning…' : 'Phone NFC' }}</span>
    </button>

    <button
      type="button"
      class="scan-btn"
      :class="{ active: espScanning }"
      :disabled="!device.canUseEsp32.value"
      :title="espTitle"
      @click="espScan"
    >
      <svg class="scan-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <rect x="7" y="7" width="10" height="10" rx="1.5" />
        <path d="M9.5 12h5M12 9.5v5" />
        <path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4" />
      </svg>
      <span>{{ espScanning ? 'Scanning…' : 'ESP32' }}</span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useDevice } from '../composables/useDevice'
import { useSerialStore } from '../stores/serial'
import { useDialog } from '../composables/useDialog'

const emit = defineEmits(['scan'])

const device = useDevice()
const serial = useSerialStore()
const dialog = useDialog()

const phoneScanning = ref(false)
const espScanning = ref(false)
let nfcAbort = null
let nfcTimeout = null
let nfcTimedOut = false

const phoneTitle = computed(() => {
  if (!device.nfcSupported.value) return 'Web NFC is not supported in this browser'
  if (!device.isMobile) return 'Phone NFC is only available on an Android phone'
  return 'Scan using this phone\u2019s NFC reader'
})
const espTitle = computed(() => {
  if (!device.serialSupported.value) return 'Web Serial is not supported in this browser'
  if (device.isMobile) return 'ESP32 scanner works on a desktop/laptop browser'
  return 'Scan using the ESP32-S3 USB scanner'
})

async function phoneScan() {
  if (phoneScanning.value) return
  if (!device.canUsePhoneNfc.value) { dialog.alertMsg(phoneTitle.value); return }
  phoneScanning.value = true
  nfcAbort = new AbortController()
  nfcTimedOut = false

  nfcTimeout = setTimeout(() => {
    nfcTimedOut = true
    nfcAbort.abort()
    phoneScanning.value = false
    dialog.alertMsg('No NFC tag detected. Hold the card/phone against the device.', 'Scan Timeout')
  }, 15000)

  try {
    const ndef = new NDEFReader()
    await ndef.scan({ signal: nfcAbort.signal })

    ndef.addEventListener('reading', ({ message, serialNumber }) => {
      clearTimeout(nfcTimeout)
      phoneScanning.value = false
      for (const r of message.records) {
        if (r.recordType === 'text') {
          const dec = new TextDecoder(r.encoding || 'utf-8')
          emit('scan', dec.decode(r.data).trim())
          return
        }
      }
      const uid = serialNumber || 'unknown'
      dialog.alertMsg(`Tag UID: ${uid}\nNo patient ID found — this is a physical card, not a Cura digital card.`, 'NFC Scan')
    })

    ndef.addEventListener('readingerror', () => {
      clearTimeout(nfcTimeout)
      phoneScanning.value = false
      dialog.alertMsg('Could not read patient ID from this tag.', 'Scan Failed')
    })
  } catch (e) {
    clearTimeout(nfcTimeout)
    phoneScanning.value = false
    if (!nfcTimedOut) {
      if (e.name === 'AbortError') return
      dialog.alertMsg('NFC scan failed. Make sure NFC is enabled and the card is held steady.', 'NFC Error')
    }
  }
}

async function espScan() {
  if (espScanning.value) return
  if (!device.canUseEsp32.value) { dialog.alertMsg(espTitle.value); return }
  if (!serial.connected) {
    const ok = await dialog.confirm('ESP32 scanner is not connected. Connect it now?', 'Connect ESP32', 'Connect')
    if (!ok) return
    const opened = await serial.connect()
    if (!opened) { dialog.alertMsg(serial.error || 'Connection failed.', 'ESP32'); return }
  }
  espScanning.value = true
  const uid = await serial.readOnce(15000)
  espScanning.value = false
  if (!uid) {
    dialog.alertMsg('No tag detected. Tap the card on the ESP32 reader.', 'Scan Timeout')
  } else {
    emit('scan', uid)
  }
}

onUnmounted(() => {
  clearTimeout(nfcTimeout)
  if (nfcAbort) nfcAbort.abort()
})
</script>

<style scoped>
.scanbar {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}
.scan-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 14px;
  border-radius: 14px;
  border: 1.5px solid var(--border);
  background: var(--bg-card);
  color: var(--text);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(20px);
  transition: all 0.2s;
  white-space: nowrap;
}
.scan-btn:hover:not(:disabled) { transform: translateY(-1px); border-color: var(--ios-blue); color: var(--ios-blue); }
.scan-btn.active { border-color: var(--ios-blue); color: var(--ios-blue); background: rgba(0,122,255,0.12); }
.scan-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  filter: grayscale(0.4);
}
.scan-icon { width: 18px; height: 18px; }
</style>