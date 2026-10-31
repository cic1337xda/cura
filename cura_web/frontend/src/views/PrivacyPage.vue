<template>
  <div class="page-content">
    <div class="header">
      <router-link to="/" class="btn btn-sm btn-outline">← Back</router-link>
    </div>

    <div class="glass p-6" style="max-width: 820px; margin: 0 auto;">
      <h1>Privacy &amp; Data Protection Policy</h1>
      <p class="text-secondary" style="font-size: 13px; margin: 6px 0 24px;">
        Last updated: October {{ currentYear }} • Cura. Hospital Management Information System
      </p>

      <section class="privacy-section">
        <h2>1. Purpose &amp; Medical Record Keeping</h2>
        <p>
          Cura. HMS collects and processes patient demographics, medical history, vital signs, diagnostic results,
          digital prescriptions, and attending practitioner notes solely for the administration of clinical care,
          treatment planning, and hospital asset tracking.
        </p>
      </section>

      <section class="privacy-section mt-4">
        <h2>2. NFC &amp; Smart Card Identifiers</h2>
        <p>
          Physical NFC cards, Malaysian MyKad RFID chip UIDs (`CF289949`), and digital Host Card Emulation (HCE)
          tokens are utilized strictly as hardware index identifiers. No private medical diagnoses or raw clinical notes
          are stored unencrypted on physical tag chips.
        </p>
      </section>

      <section class="privacy-section mt-4">
        <h2>3. Access Control &amp; Confidentiality</h2>
        <p>
          Access to clinical data is governed by strict Role-Based Access Control (RBAC). Only authenticated healthcare
          personnel and authorized system administrators are permitted to review or amend electronic health records.
        </p>
      </section>

      <section class="privacy-section mt-4">
        <h2>4. Authentication Sessions</h2>
        <p>
          System access is authenticated via JSON Web Tokens (JWT). Sessions expire automatically after predefined idle
          intervals to prevent unauthorized terminal access.
        </p>
      </section>

      <section class="privacy-section mt-4">
        <h2>5. Compliance</h2>
        <p>
          Cura. HMS adheres to applicable clinical confidentiality standards and the Malaysia Personal Data
          Protection Act (PDPA) governing the lawful storage and protection of sensitive personal health data.
        </p>
      </section>

      <div class="mt-6 pt-4" style="border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
        <span class="text-secondary">© {{ currentYear }} Cura. HMS. All rights reserved.</span>
        <router-link to="/dashboard" class="btn btn-sm">Go to Dashboard</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
const currentYear = new Date().getFullYear()
</script>

<style scoped>
.privacy-section h2 {
  font-size: 17px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--ios-blue);
}
.privacy-section p {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
}
.pt-4 {
  padding-top: 16px;
}
</style>
