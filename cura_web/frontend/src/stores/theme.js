import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const dark = ref(localStorage.getItem('cura_dark') === 'true')

  function toggle() {
    dark.value = !dark.value
    localStorage.setItem('cura_dark', String(dark.value))
    apply()
  }

  function set(value) {
    dark.value = !!value
    localStorage.setItem('cura_dark', String(dark.value))
    apply()
  }

  function apply() {
    document.documentElement.classList.toggle('dark', dark.value)
  }

  apply()
  return { dark, toggle, set }
})