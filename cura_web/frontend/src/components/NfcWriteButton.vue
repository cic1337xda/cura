<template>
  <button
    type="button"
    class="btn btn-sm write-card-btn"
    :class="{ writing: waiting }"
    :disabled="disabled || waiting"
    :title="disabledReason || 'Write this UID to an NFC card using the ESP32-S3'"
    @click="write"
  >
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px;">
      <rect x="3" y="5" width="12" height="16" rx="1.6" />
      <line x1="6" y1="17" x2="10" y2="17" />
      <path d="M15 9l4 4M19 9l-4 4" />
    </svg>
    {{ waiting ? 'Waiting for card…' : label }}
  </button>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDevice } from '../composables/useDevice'
import { useSerialStore } from '../stores/serial'
import { useDialog } from '../composables/useDialog'

const props = defineProps({
  uid: { type: String, default: '' },
  label: { type: String, default: 'Write Card' },
})

const device = useDevice()
const serial = useSerialStore()
const dialog = useDialog()

const waiting = ref(false)
let offStatus = null

const valid = computed(() => /^[0-9A-Fa-f]{8}$/.test((props.uid || '').trim()))
const disabled = computed(() => !device.canUseEsp32.value || !valid.value)

const disabledReason = computed(() => {
  if (!valid.value) return 'UID is not a valid 8-character HEX code'
  if (!device.canUseEsp32.value) return 'Card writing requires the ESP32-S3 on a desktop/laptop browser'
  return ''
})

onMounted(() => {
  offStatus = serial.onStatus(({ state, message }) => {
    if (state === 'success' || state === 'error') {
      waiting.value = false
      dialog.alertMsg(message, state === 'success' ? 'Write Successful' : 'Write Failed')
    }
  })
})

onUnmounted(() => { if (offStatus) offStatus() })

async function write() {
  if (disabled.value) { dialog.alertMsg(disabledReason.value); return }
  if (!serial.connected) {
    const ok = await dialog.confirm('ESP32 scanner is not connected. Connect it now?', 'Connect ESP32', 'Connect')
    if (!ok) return
    const opened = await serial.connect()
    if (!opened) { dialog.alertMsg(serial.error || 'Connection failed.', 'ESP32'); return }
  }

  const res = await serial.writeUid(props.uid)
  if (!res.ok) {
    dialog.alertMsg(res.message, 'Write Failed')
  } else {
    waiting.value = true
  }
}
</script>

<style scoped>
.write-card-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: var(--ios-blue);
  color: #fff;
  border: none;
}
.write-card-btn.writing {
  background: var(--ios-orange);
  cursor: progress;
}
.write-card-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>