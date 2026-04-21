/**
 * 主题 composable
 * 管理亮/暗模式（含跟随系统）与主色方案，状态持久化到 localStorage，
 * 通过切换 html 根元素上的 `.dark` 和 `.theme-xxx` 类驱动 Tailwind 设计 token
 */
import { ref, watchEffect } from 'vue'
import { usePreferredDark, useStorage } from '@vueuse/core'

/** 可选主色方案；neutral 为默认无额外 class */
type ColorTheme = 'neutral' | 'blue' | 'green' | 'rose' | 'orange' | 'violet' | 'slate'

const COLOR_THEMES: ColorTheme[] = ['neutral', 'blue', 'green', 'rose', 'orange', 'violet', 'slate']

/**
 * 使用/控制主题
 * @returns isDark(当前是否暗色)、theme(用户选择 light/dark/system)、切换方法、主色及其 setter
 */
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
      // 先清除已有的主色 class，再按当前选择添加，避免叠加
      COLOR_THEMES.forEach(t => document.documentElement.classList.remove(`theme-${t}`))
      // neutral 作为默认主色不需要添加 class
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
