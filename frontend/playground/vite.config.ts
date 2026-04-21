import { resolve } from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@dwydev/eui/theme': resolve(__dirname, '../eui/src/theme/index.css'),
      '@dwydev/eui': resolve(__dirname, '../eui/src/index.ts'),
      '@': resolve(__dirname, '../eui/src'),
    },
  },
  assetsInclude: ['**/*.md'],
  server: {
    port: 7188,
  },
})
