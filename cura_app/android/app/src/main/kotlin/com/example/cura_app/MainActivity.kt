package com.example.cura_app

import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import android.nfc.NfcAdapter
import android.nfc.cardemulation.CardEmulation
import android.content.ComponentName
import android.os.Bundle
import android.util.Log

class MainActivity: FlutterActivity() {
    private var nfcAdapter: NfcAdapter? = null
    private var cardEmulationManager: CardEmulation? = null
    private var hceServiceComponent: ComponentName? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        nfcAdapter = NfcAdapter.getDefaultAdapter(this)
        if (nfcAdapter != null) {
            cardEmulationManager = CardEmulation.getInstance(nfcAdapter)
            hceServiceComponent = ComponentName(this, MyHceService::class.java)
        }
    }

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "com.example.cura_app/hce")
            .setMethodCallHandler { call, result ->
                if (call.method == "setPatientId") {
                    val patientId = call.argument<String>("patientId") ?: ""
                    MyHceService.patientId = patientId
                    Log.d("MainActivity", "Patient ID updated: $patientId")
                    result.success(true)
                } else {
                    result.notImplemented()
                }
            }
    }

    override fun onResume() {
        super.onResume()
        if (nfcAdapter != null && cardEmulationManager != null && hceServiceComponent != null) {
            val success = cardEmulationManager?.setPreferredService(this, hceServiceComponent)
            Log.d("MainActivity", "setPreferredService result: $success")
            if (success == false) {
                Log.w("MainActivity", "Failed to set preferred HCE service. Is another app the default?")
            }
        }
    }

    override fun onPause() {
        super.onPause()
        if (nfcAdapter != null && cardEmulationManager != null) {
            cardEmulationManager?.unsetPreferredService(this)
            Log.d("MainActivity", "HCE preferred service unset")
        }
    }
}