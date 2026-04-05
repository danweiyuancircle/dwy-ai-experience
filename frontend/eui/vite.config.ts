import { resolve } from 'node:path'
import vue from '@vitejs/plugin-vue'
import dts from 'vite-plugin-dts'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [
    vue(),
    dts({
      tsconfigPath: './tsconfig.json',
      outDir: 'dist',
      cleanVueFileName: true,
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      formats: ['es'],
      fileName: 'index',
    },
    rollupOptions: {
      external: [
        'vue',
        'reka-ui',
        '@floating-ui/vue',
        '@tanstack/vue-table',
        '@vueuse/core',
        'class-variance-authority',
        'clsx',
        'embla-carousel',
        'embla-carousel-vue',
        'lucide-vue-next',
        'tailwind-merge',
        'vaul-vue',
        'vee-validate',
        '@vee-validate/zod',
        'zod',
        '@internationalized/date',
      ],
      output: {
        preserveModules: true,
        preserveModulesRoot: 'src',
      },
    },
    cssCodeSplit: true,
  },
})
