package com.example.cura_app

import android.nfc.cardemulation.HostApduService
import android.os.Bundle
import android.nfc.NfcAdapter
import android.util.Log

class MyHceService : HostApduService() {

    companion object {
        var patientId: String = "103110313131"
    }

    private var ndefSelected = false

    override fun onCreate() {
        super.onCreate()
        if (android.os.Build.VERSION.SDK_INT >= 35) {
            try {
                val method = HostApduService::class.java.getDeclaredMethod(
                    "setObserveModeEnabled", Boolean::class.javaPrimitiveType
                )
                method.isAccessible = true
                method.invoke(this, false)
                Log.d("MyHceService", "Observe mode disabled via HostApduService hidden API")
            } catch (e: NoSuchMethodException) {
                Log.w("MyHceService", "setObserveModeEnabled not found on HostApduService")
                disableObserveModeViaNfcAdapter()
            } catch (e: Exception) {
                Log.e("MyHceService", "HostApduService reflection failed: ${e.message}")
                disableObserveModeViaNfcAdapter()
            }
        }
    }

    private fun disableObserveModeViaNfcAdapter() {
        try {
            val adapter = NfcAdapter.getDefaultAdapter(this)
            if (adapter != null) {
                val method = adapter.javaClass.getDeclaredMethod(
                    "setObserveModeEnabled", Boolean::class.javaPrimitiveType
                )
                method.isAccessible = true
                method.invoke(adapter, false)
                Log.d("MyHceService", "Observe mode disabled via NfcAdapter")
            }
        } catch (e: Exception) {
            Log.e("MyHceService", "NfcAdapter reflection also failed: ${e.message}")
        }
    }

    override fun processCommandApdu(commandApdu: ByteArray?, extras: Bundle?): ByteArray {
        if (commandApdu == null) return byteArrayOf(0x6A.toByte(), 0x82.toByte())

        val hex = commandApdu.joinToString(" ") { "%02X".format(it) }
        Log.d("MyHceService", hex)

        // ─── SELECT Cura AID (F222222222) ────────────────────────────────
        if (isSelectAid(commandApdu, byteArrayOf(0xF2.toByte(), 0x22, 0x22, 0x22, 0x22))) {
            val payload = patientId.toByteArray(Charsets.UTF_8)
            Log.d("MyHceService", "→ patientId=$patientId")
            return payload + byteArrayOf(0x90.toByte(), 0x00.toByte())
        }

        // ─── SELECT NDEF AID (D2760000850101) ───────────────────────────
        if (isSelectAid(commandApdu, byteArrayOf(0xD2.toByte(), 0x76, 0x00, 0x00, 0x85.toByte(), 0x01, 0x01))) {
            Log.d("MyHceService", "→ NDEF FCI")
            ndefSelected = false
            return byteArrayOf(
                0x6F.toByte(), 0x11, 0x84.toByte(), 0x07, 0xD2.toByte(), 0x76, 0x00, 0x00, 0x85.toByte(), 0x01, 0x01,
                0xA5.toByte(), 0x06, 0x80.toByte(), 0x02, 0x00.toByte(), 0xFF.toByte(), 0x81.toByte(), 0x02, 0xE1.toByte(), 0x03,
                0x90.toByte(), 0x00.toByte()
            )
        }

        // ─── SELECT File ID (E1 03) ─────────────────────────────────────
        if (commandApdu.size >= 7 && commandApdu[0] == 0x00.toByte() && commandApdu[1] == 0xA4.toByte() &&
            commandApdu[4] == 0x02.toByte() && commandApdu[5] == 0xE1.toByte() && commandApdu[6] == 0x03.toByte()) {
            Log.d("MyHceService", "→ SELECT EF E103")
            ndefSelected = true
            return byteArrayOf(0x90.toByte(), 0x00.toByte())
        }

        // ─── READ BINARY ─────────────────────────────────────────────────
        if (commandApdu[0] == 0x00.toByte() && commandApdu[1] == 0xB0.toByte()) {
            val offset = ((commandApdu[2].toInt() and 0xFF) shl 8) or (commandApdu[3].toInt() and 0xFF)
            val len = if (commandApdu.size >= 5) (commandApdu[4].toInt() and 0xFF) else 0
            Log.d("MyHceService", "→ READ BINARY off=$offset len=$len ndef=$ndefSelected")

            if (!ndefSelected) {
                // CC file
                val ccFile = byteArrayOf(
                    0x00.toByte(), 0x0F.toByte(), 0x20.toByte(), 0x00.toByte(),
                    0xFF.toByte(), 0x00.toByte(), 0xFF.toByte(),
                    0x04.toByte(), 0x06.toByte(), 0xE1.toByte(), 0x03.toByte(),
                    0x00.toByte(), 0x00.toByte(), 0x00.toByte(), 0x00.toByte()
                )
                val n = if (offset + len > ccFile.size) ccFile.size - offset else len
                val slice = ccFile.copyOfRange(offset, offset + n)
                return slice + byteArrayOf(0x90.toByte(), 0x00.toByte())
            } else {
                // NDEF file — some readers expect raw NDEF without NLEN prefix
                val ndef = buildNdefRecord(patientId)

                if (offset == 0 && len == 2) {
                    // Reader probing for NLEN — return NDEF message size
                    return byteArrayOf(((ndef.size shr 8) and 0xFF).toByte(), (ndef.size and 0xFF).toByte(), 0x90.toByte(), 0x00.toByte())
                }

                val n = if (offset + len > ndef.size) ndef.size - offset else len
                val slice = ndef.copyOfRange(offset, offset + n)
                val resp = slice + byteArrayOf(0x90.toByte(), 0x00.toByte())
                Log.d("MyHceService", "→ NDEF RESP [${resp.size}b] no NLEN: ${resp.joinToString(" "){ "%02X".format(it) }}")
                return resp
            }
        }

        return byteArrayOf(0x6F.toByte(), 0x00.toByte())
    }

    private fun isSelectAid(apdu: ByteArray, aid: ByteArray): Boolean {
        if (apdu.size < 5 + aid.size) return false
        if (apdu[0] != 0x00.toByte() || apdu[1] != 0xA4.toByte() || apdu[2] != 0x04.toByte()) return false
        if (apdu[4] != aid.size.toByte()) return false
        for (i in aid.indices) if (apdu[5 + i] != aid[i]) return false
        return true
    }

    private fun buildNdefRecord(text: String): ByteArray {
        val tb = text.toByteArray(Charsets.UTF_8)
        val lb = "en".toByteArray(Charsets.UTF_8)
        val pl = 1 + lb.size + tb.size
        val rec = ByteArray(3 + 1 + pl)
        rec[0] = 0xD1.toByte(); rec[1] = 0x01.toByte(); rec[2] = pl.toByte()
        rec[3] = 'T'.code.toByte(); rec[4] = 0x02.toByte()
        System.arraycopy(lb, 0, rec, 5, lb.size)
        System.arraycopy(tb, 0, rec, 5 + lb.size, tb.size)
        return rec
    }

    override fun onDeactivated(reason: Int) {
        Log.d("MyHceService", "Deactivated. Reason: $reason")
    }
}