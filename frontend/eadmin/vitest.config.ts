/**
 * admin-shell 单测配置
 * 同时覆盖纯装配函数与管理组合组件，保留真实 EUI 交互测试。
 */
import { fileURLToPath } from 'node:url'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    dedupe: ['vue', 'vue-router', '@dwydev/eui'],
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    environment: 'jsdom',
    include: ['tests/**/*.test.ts'],
    server: {
      deps: { inline: ['@dwydev/ekit', '@dwydev/eui', 'dayjs'] },
    },
  },
})
