/**
 * @dwydev/admin-kit 库构建
 * 对齐 eui：ES + preserveModules + vue + dts；peer 全部 external。
 */
import { resolve } from 'node:path'
import vue from '@vitejs/plugin-vue'
import dts from 'vite-plugin-dts'
import { defineConfig } from 'vite'
import { DiagnosticCategory } from 'typescript'

export default defineConfig({
  plugins: [
    vue(),
    dts({
      tsconfigPath: './tsconfig.json',
      outDir: 'dist',
      cleanVueFileName: true,
      // 声明诊断不能只打印后仍报告 build 成功，否则消费方才会发现丢类型。
      afterDiagnostic(diagnostics) {
        if (diagnostics.some(diagnostic => diagnostic.category === DiagnosticCategory.Error)) {
          throw new Error('admin-kit declaration generation failed')
        }
      },
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
        'components/index': resolve(__dirname, 'src/components/index.ts'),
        'composables/index': resolve(__dirname, 'src/composables/index.ts'),
        'paged-list/index': resolve(__dirname, 'src/paged-list/index.ts'),
        'components/status/tone': resolve(__dirname, 'src/components/status/tone.ts'),
      },
      formats: ['es'],
      fileName: (_format, entryName) => `${entryName}.js`,
      cssFileName: 'style',
    },
    rollupOptions: {
      external: [
        'vue',
        'vue-router',
        '@dwydev/eui',
        '@dwydev/ekit',
        'lucide-vue-next',
      ],
      output: {
        // 由 bundler 的模板清理 SFC 虚拟模块名；自定义 lib.fileName 会保留 ? 查询串。
        entryFileNames: '[name].js',
        preserveModules: true,
        preserveModulesRoot: 'src',
      },
    },
  },
})
