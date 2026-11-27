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
      entry: {
        index: resolve(__dirname, 'src/index.ts'),
        'charts/index': resolve(__dirname, 'src/charts/index.ts'),
        'motion/index': resolve(__dirname, 'src/motion/index.ts'),
      },
      formats: ['es'],
      fileName: (_, entryName) => entryName + '.js',
    },
    rollupOptions: {
      external: [
        'vue',
        'reka-ui',
        '@tanstack/vue-table',
        '@tanstack/vue-virtual',
        /^@unovis\/vue(?:\/|$)/,
        '@vueuse/core',
        'class-variance-authority',
        'clsx',
        'embla-carousel',
        'embla-carousel-vue',
        'lucide-vue-next',
        'motion-v',
        'tailwind-merge',
        'vee-validate',
        '@vee-validate/zod',
        'vue-sonner',
        'zod',
        '@internationalized/date',
      ],
      output: {
        // 由 bundler 的模板清理 SFC 虚拟模块名，避免产物路径包含查询串。
        entryFileNames: '[name].js',
        preserveModules: true,
        preserveModulesRoot: 'src',
      },
    },
    cssCodeSplit: true,
  },
})
