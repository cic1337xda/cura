// Entity → 4-char HEX NFC prefix. Must match backend `app/core/idgen.py`.
export const ID_PREFIX = {
  patient: 'C00A',
  doctor: 'C01A',
  prescription: 'C02A',
  lab: 'C03A',
  vitals: 'C04A',
  record: 'C05A',
  surgery: 'C06A',
  vendor: 'C07A',
  account: 'C08A',
  payroll: 'C09A',
}

// Build the full 8-char UID from a prefix + patient number.
export function formatId(prefix, n) {
  return `${prefix}${String(n).padStart(4, '0')}`
}

// Extract the numeric tail from a full UID (e.g. 'C00A0001' -> 1).
export function parseId(prefix, id) {
  if (!id || typeof id !== 'string') return ''
  if (!id.startsWith(prefix)) return ''
  return id.slice(prefix.length)
}