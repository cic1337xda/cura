<template>
  <div class="login-wrap">
    <div class="login-card glass">
      <h2>{{ isDoctor ? 'Doctor Login' : 'Admin Login' }}</h2>
      <p class="sub">{{ isDoctor ? 'Sign in with your employee number' : 'Sign in to manage the hospital system' }}</p>
      <form @submit.prevent="handleLogin">
        <label class="input-label">{{ isDoctor ? 'EMPLOYEE NUMBER' : 'EMAIL' }}</label>
        <input v-if="isDoctor" v-model="form.employee_number" class="input" placeholder="e.g. YDS7L" required />
        <input v-else v-model="form.email" type="email" class="input" placeholder="admin@hospital.com" required />
        <div style="margin-top: 16px;">
          <label class="input-label">PASSWORD</label>
          <input v-model="form.password" type="password" class="input" placeholder="Enter password" required />
        </div>
        <div v-if="error" style="color: var(--ios-red); font-size: 13px; margin-top: 12px;">{{ error }}</div>
        <button type="submit" class="btn" style="width: 100%; margin-top: 24px;" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>
      <div style="margin-top: 16px; text-align: center; font-size: 13px;">
        <a href="#" @click.prevent="isDoctor = !isDoctor">{{ isDoctor ? 'Admin login instead' : 'Doctor login instead' }}</a>
      </div>
      <div style="margin-top: 12px; text-align: center; font-size: 13px;">
        <router-link to="/">← Back to Home</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const isDoctor = ref(false)
const loading = ref(false)
const error = ref('')
const form = ref({ email: '', employee_number: '', password: '' })

onMounted(() => { isDoctor.value = route.query.role === 'doctor' })

async function handleLogin() {
  loading.value = true; error.value = ''
  try {
    const url = isDoctor.value ? '/auth/doctor/login' : '/auth/admin/login'
    const payload = isDoctor.value
      ? { employee_number: form.value.employee_number, password: form.value.password }
      : { email: form.value.email, password: form.value.password }
    const { data } = await axios.post(url, payload)
    localStorage.setItem('cura_token', data.access_token)
    localStorage.setItem('cura_role', data.role)
    axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>