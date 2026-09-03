<template>
  <div>
    <div class="orbs"><div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div></div>

    <button v-if="!isGuest" class="menu-btn" @click="sidebarOpen = !sidebarOpen">☰</button>

    <div class="sidebar-overlay" v-if="sidebarOpen" @click="sidebarOpen = false"></div>
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-header">
        <h2>Cura<span>.</span></h2>
        <button class="sidebar-close" @click="sidebarOpen = false">✕</button>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="sidebar-link" :class="{ active: $route.path === '/dashboard' }" @click="sidebarOpen = false">Dashboard</router-link>
        <router-link to="/patients" class="sidebar-link" :class="{ active: $route.path.startsWith('/patients') }" @click="sidebarOpen = false">Patients</router-link>
        <router-link to="/doctors" class="sidebar-link" :class="{ active: $route.path.startsWith('/doctors') }" @click="sidebarOpen = false">Doctors</router-link>
        <router-link to="/pharmacy" class="sidebar-link" :class="{ active: $route.path.startsWith('/pharmacy') }" @click="sidebarOpen = false">Pharmacy</router-link>
        <router-link to="/prescriptions" class="sidebar-link" :class="{ active: $route.path === '/prescriptions' }" @click="sidebarOpen = false">Prescriptions</router-link>
        <router-link to="/laboratory" class="sidebar-link" :class="{ active: $route.path === '/laboratory' }" @click="sidebarOpen = false">Laboratory</router-link>
        <router-link to="/vitals" class="sidebar-link" :class="{ active: $route.path === '/vitals' }" @click="sidebarOpen = false">Vitals</router-link>
        <router-link to="/medical-records" class="sidebar-link" :class="{ active: $route.path === '/medical-records' }" @click="sidebarOpen = false">Med Records</router-link>
        <router-link to="/surgery" class="sidebar-link" :class="{ active: $route.path === '/surgery' }" @click="sidebarOpen = false">Surgery</router-link>
        <router-link to="/equipment" class="sidebar-link" :class="{ active: $route.path === '/equipment' }" @click="sidebarOpen = false">Equipment</router-link>
        <router-link to="/vendors" class="sidebar-link" :class="{ active: $route.path === '/vendors' }" @click="sidebarOpen = false">Vendors</router-link>
        <router-link to="/accounts" class="sidebar-link" :class="{ active: $route.path === '/accounts' }" @click="sidebarOpen = false">Accounts</router-link>
        <router-link to="/payrolls" class="sidebar-link" :class="{ active: $route.path === '/payrolls' }" @click="sidebarOpen = false">Payrolls</router-link>
        <router-link to="/settings" class="sidebar-link" :class="{ active: $route.path === '/settings' }" @click="sidebarOpen = false">Settings</router-link>
      </nav>
      <div class="sidebar-footer"><a href="#" @click.prevent="logout">Sign Out</a></div>
    </aside>

    <div class="page"><router-view /></div>
    <GlassDialog />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useThemeStore } from './stores/theme'
import GlassDialog from './components/GlassDialog.vue'
const theme = useThemeStore()
const router = useRouter()
const route = useRoute()
const sidebarOpen = ref(false)
const isGuest = computed(() => route.meta.guest === true)

function logout() {
  localStorage.removeItem('cura_token')
  localStorage.removeItem('cura_role')
  sidebarOpen.value = false
  router.push('/login')
}
</script>