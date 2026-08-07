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
      '@dwydev/ekit': resolve(__dirname, '../ekit/src/index.ts'),
      // 开发期直连源码，免先 build admin
      '@dwydev/admin-kit/theme': resolve(__dirname, '../admin/src/theme.css'),
      '@dwydev/admin-kit': resolve(__dirname, '../admin/src/index.ts'),
      '@': resolve(__dirname, '../eui/src'),
    },
    // 避免 admin 与 playground 各解析一份 vue-router 导致 inject 丢失
    dedupe: ['vue', 'vue-router'],
  },
  assetsInclude: ['**/*.md'],
  server: {
    port: 7188,
  },
})
