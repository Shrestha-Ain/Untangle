import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ThemeMode = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
  // Read initial theme from localStorage or system preference
  const saved = localStorage.getItem('untangle_theme') as ThemeMode | null
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  const initialTheme: ThemeMode = saved || (prefersDark ? 'dark' : 'light')

  const currentTheme = ref<ThemeMode>(initialTheme)

  function applyTheme(theme: ThemeMode) {
    currentTheme.value = theme
    localStorage.setItem('untangle_theme', theme)
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  function toggleTheme() {
    applyTheme(currentTheme.value === 'dark' ? 'light' : 'dark')
  }

  // Initialize on load
  applyTheme(initialTheme)

  return {
    currentTheme,
    theme: currentTheme,
    isDark: () => currentTheme.value === 'dark',
    toggleTheme,
    setTheme: applyTheme,
  }
})
