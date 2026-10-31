import { defineStore } from 'pinia'
import { ref } from 'vue'

let port = null
let writer = null
let reader = null
let buffer = ''

const readListeners = new Set()
const statusListeners = new Set()
const closeListeners = new Set()

export const useSerialStore = defineStore('serial', () => {
  const supported = ref(typeof navigator !== 'undefined' && 'serial' in navigator)
  const connected = ref(false)
  const connecting = ref(false)
  const error = ref('')
  const portName = ref('')
  const lastUid = ref('')
  const lastWriteStatus = ref(null) // { state: 'pending'|'success'|'error', message }

  const isArmed = ref(false)

  function emitRead(uid) {
    lastUid.value = uid
    readListeners.forEach((cb) => cb(uid))
  }
  function emitStatus(state, message) {
    if (state === 'armed') isArmed.value = true
    lastWriteStatus.value = { state, message, at: Date.now() }
    statusListeners.forEach((cb) => cb({ state, message }))
  }
  function emitClose() {
    connected.value = false
    portName.value = ''
    isArmed.value = false
    closeListeners.forEach((cb) => cb())
  }

  async function processLine(line) {
    const text = line.trim()
    if (!text) return

    if (text.startsWith('[WEB_READ]:')) {
      const uid = text.substring(text.indexOf(':') + 1).trim()
      if (uid) emitRead(uid)
    } else if (text === '[UI_ARMED]' || text.startsWith('[ARMED]')) {
      emitStatus('armed', 'Device armed! Please TAP your tag on the reader now...')
    } else if (text === '[UI_SUCCESS]') {
      isArmed.value = false
      emitStatus('success', 'Card successfully programmed! UID verified.')
    } else if (text === '[UI_FAILED]') {
      isArmed.value = false
      emitStatus('error', 'Write failed. Card might be locked or removed too early.')
    } else if (text.startsWith('[ERROR]')) {
      emitStatus('error', text.slice(8).trim() || 'Device reported an error.')
    }
  }

  async function readLoop() {
    while (connected.value && reader) {
      try {
        const { value, done } = await reader.read()
        if (done) break
        buffer += value
        const lines = buffer.split('\n')
        buffer = lines.pop()
        for (const line of lines) await processLine(line)
      } catch (e) {
        break
      }
    }
    emitClose()
  }

  async function openPort(p) {
    await p.open({ baudRate: 115200 })
    port = p
    const info = p.getInfo?.()
    portName.value = (info && (info.usbProductName || info.usbVendorId)) ? info.usbProductName || `ESP32 (${info.usbVendorId.toString(16)})` : 'ESP32-S3'

    writer = p.writable.getWriter()
    const decoder = new TextDecoderStream()
    p.readable.pipeTo(decoder.writable)
    reader = decoder.readable.getReader()

    connected.value = true
    error.value = ''
    isArmed.value = false
    readLoop()
  }

  async function connect() {
    if (!supported.value) {
      error.value = 'Web Serial is not supported by this browser.'
      return false
    }
    connecting.value = true
    error.value = ''
    try {
      const p = await navigator.serial.requestPort()
      await openPort(p)
      return true
    } catch (e) {
      if (e.name !== 'NotFoundError') {
        error.value = 'Connection failed. Ensure the ESP32-S3 is plugged in.'
      }
      return false
    } finally {
      connecting.value = false
    }
  }

  async function connectTo(p) {
    if (connected.value) return true
    connecting.value = true
    error.value = ''
    try {
      await openPort(p)
      return true
    } catch (e) {
      error.value = 'Could not open the selected port.'
      return false
    } finally {
      connecting.value = false
    }
  }

  function savedPorts() {
    if (!supported.value) return []
    try {
      return navigator.serial.getPorts()
    } catch (e) {
      return []
    }
  }

  function portLabel(p) {
    try {
      const info = p.getInfo?.()
      if (info && info.usbProductName) return info.usbProductName
      if (info && info.usbVendorId) return `ESP32 (${info.usbVendorId.toString(16)})`
    } catch (e) {}
    return 'Serial device'
  }

  async function disconnect() {
    try {
      if (reader) { try { await reader.cancel() } catch (e) {} reader = null }
      if (writer) { try { await writer.close() } catch (e) {} writer = null }
      if (port) { try { await port.close() } catch (e) {} port = null }
    } catch (e) {}
    emitClose()
  }

  async function writeUid(uid) {
    if (!connected.value || !writer) {
      return { ok: false, message: 'Not connected. Connect the ESP32 first.' }
    }
    const clean = String(uid).trim().toUpperCase().replace(/[^0-9A-F]/g, '')
    if (clean.length !== 8) {
      return { ok: false, message: 'Invalid UID! Must be exactly 8 HEX characters.' }
    }
    try {
      const encoder = new TextEncoder()
      await writer.write(encoder.encode(`WRITE ${clean}\n`))
      emitStatus('armed', 'Command sent. Tap your card on the reader now...')
      return { ok: true }
    } catch (e) {
      emitStatus('error', 'Failed to send write command.')
      return { ok: false, message: 'Failed to send write command.' }
    }
  }

  function readOnce(timeoutMs = 15000) {
    return new Promise((resolve) => {
      let done = false
      const finish = (uid) => { if (done) return; done = true; clearTimeout(timer); readListeners.delete(handler); resolve(uid) }
      const timer = setTimeout(() => finish(null), timeoutMs)
      const handler = (uid) => finish(uid)
      readListeners.add(handler)
    })
  }

  function onRead(cb) { readListeners.add(cb); return () => readListeners.delete(cb) }
  function onStatus(cb) { statusListeners.add(cb); return () => statusListeners.delete(cb) }
  function onClose(cb) { closeListeners.add(cb); return () => closeListeners.delete(cb) }

  return {
    supported, connected, connecting, error, portName, lastUid, lastWriteStatus, isArmed,
    connect, connectTo, disconnect, writeUid, savedPorts, portLabel, readOnce,
    onRead, onStatus, onClose,
  }
})