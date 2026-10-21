import { fileURLToPath } from 'node:url'
import vue from '@vitejs/plugin-vue'
import dts from 'vite-plugin-dts'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue(), dts({ tsconfigPath: './tsconfig.json', cleanVueFileName: true })],
  build: {
    lib: { entry: fileURLToPath(new URL('./src/index.ts', import.meta.url)), formats: ['es'], fileName: 'index' },
    rollupOptions: { external: ['vue', '@dwydev/eui', 'lucide-vue-next'] },
  },
})
