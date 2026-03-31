import { resolve } from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      // Resolve EUI JS from source for instant HMR during development
      '@danweiyuan/eui/theme': resolve(__dirname, '../packages/eui/src/theme/index.css'),
      '@danweiyuan/eui': resolve(__dirname, '../packages/eui/src/index.ts'),
      // Internal alias for EUI components
      '@': resolve(__dirname, '../packages/eui/src'),
    },
  },
})
