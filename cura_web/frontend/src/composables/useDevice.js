import { computed } from 'vue'

// Rough device type detection used to gate the two NFC scan paths:
//  - Web NFC (NDEFReader) only exists on Android/mobile Chrome.
//  - Web Serial only exists on desktop Chrome/Edge/Opera.
let ua = ''
let touchPoints = 0
if (typeof navigator !== 'undefined') {
  ua = navigator.userAgent || ''
  touchPoints = navigator.maxTouchPoints || 0
}

const isMobile = /Android|iPhone|iPad|iPod|Windows Phone|BlackBerry|webOS/i.test(ua)

export function useDevice() {
  const nfcSupported = computed(() => typeof window !== 'undefined' && 'NDEFReader' in window)
  const serialSupported = computed(() => typeof navigator !== 'undefined' && 'serial' in navigator)

  // Phone can read NDEF but cannot write Mifare blocks; desktop uses ESP32.
  const canUsePhoneNfc = computed(() => isMobile && nfcSupported.value)
  const canUseEsp32 = computed(() => !isMobile && serialSupported.value)

  return { isMobile, nfcSupported, serialSupported, canUsePhoneNfc, canUseEsp32 }
}