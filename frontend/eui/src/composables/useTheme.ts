import { ref, watchEffect } from 'vue'
import { usePreferredDark, useStorage } from '@vueuse/core'

type ColorTheme = 'neutral' | 'blue' | 'green' | 'rose' | 'orange' | 'violet' | 'slate'

const COLOR_THEMES: ColorTheme[] = ['neutral', 'blue', 'green', 'rose', 'orange', 'violet', 'slate']

export function useTheme() {
  const prefersDark = usePreferredDark()
  const stored = useStorage<'light' | 'dark' | 'system'>('eui-theme', 'system')
  const colorTheme = useStorage<ColorTheme>('eui-color-theme', 'neutral')

  const isDark = ref(false)

  watchEffect(() => {
    isDark.value = stored.value === 'dark' || (stored.value === 'system' && prefersDark.value)
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', isDark.value)
    }
  })

  watchEffect(() => {
    if (typeof document !== 'undefined') {
      // Remove all existing color theme classes
      COLOR_THEMES.forEach(t => document.documentElement.classList.remove(`theme-${t}`))
      // Apply the selected theme (neutral has no class — it's the default)
      if (colorTheme.value !== 'neutral') {
        document.documentElement.classList.add(`theme-${colorTheme.value}`)
      }
    }
  })

  function setTheme(theme: 'light' | 'dark' | 'system') {
    stored.value = theme
  }

  function toggleDark() {
    stored.value = isDark.value ? 'light' : 'dark'
  }

  function setColorTheme(theme: ColorTheme) {
    colorTheme.value = theme
  }

  return { isDark, theme: stored, setTheme, toggleDark, colorTheme, setColorTheme }
}
