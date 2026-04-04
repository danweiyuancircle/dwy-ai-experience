import { resolve } from 'node:path'
import dts from 'vite-plugin-dts'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [
    dts({
      tsconfigPath: './tsconfig.json',
      outDir: 'dist',
    }),
  ],
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      formats: ['es'],
      fileName: 'index',
    },
    rollupOptions: {
      external: [
        'vue',
        'axios',
        'zod',
        '@vueuse/core',
        '@vueuse/shared',
        'dayjs',
        'dayjs/locale/zh-cn',
        'dayjs/plugin/relativeTime',
        'js-cookie',
        'file-saver',
        'qs',
      ],
      output: {
        preserveModules: true,
        preserveModulesRoot: 'src',
      },
    },
  },
})
