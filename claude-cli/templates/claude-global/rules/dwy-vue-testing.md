---
description: Vitest 单元测试规范
paths:
  - "**/*.test.ts"
  - "**/*.spec.ts"
  - "**/tests/**/*.ts"
---

# Vitest 单元测试规范

## 十三、测试规范（Vitest）

### 强制规则
- 使用 **Vitest** 作为测试框架，配合 **@vue/test-utils** + **happy-dom**
- 测试文件**必须放在项目根目录的 `tests/` 目录**，按模块镜像 `src/` 结构，**禁止**放在 `src/` 内
- `tsconfig.app.json` 的 `include` **只包含 `src/`**，确保打包不携带测试文件
- 测试文件命名：`*.test.ts`

### 依赖安装

```bash
pnpm add -D vitest @vue/test-utils happy-dom
```

### package.json 脚本

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run"
  }
}
```

### vitest.config.ts（独立文件，不写在 vite.config.ts 中）

```typescript
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    environment: 'happy-dom',
    include: ['tests/**/*.test.ts'],
  },
})
```

### 目录结构与导入

```
tests/
├── utils/format.test.ts        # 测试 src/utils/format.ts
├── stores/auth.test.ts         # 测试 src/stores/auth.ts
├── api/client.test.ts          # 测试 src/api/client.ts
└── router/index.test.ts        # 测试 src/router/index.ts
```

测试文件中通过 `@` 别名导入源码，**禁止**使用相对路径回溯到 `src/`：

```typescript
// ✅ 使用 @ 别名
import { formatBytes } from '@/utils/format'
import { useAuthStore } from '@/stores/auth'

// ❌ 禁止相对路径回溯
import { formatBytes } from '../../src/utils/format'
```

### 打包隔离

`tsconfig.app.json` 的 `include` 只包含 `src/`，确保 `tests/` 不会被 `vue-tsc` 编译和打包：

```json
{
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"]
}
```

**禁止**在 `tsconfig.app.json` 中 include `tests/`。

### 禁止的写法

```
# ❌ 测试文件放在 src/ 内
src/utils/format.test.ts
src/stores/__tests__/auth.test.ts
src/components/Button.test.ts

# ✅ 测试文件放在独立 tests/ 目录
tests/utils/format.test.ts
tests/stores/auth.test.ts
tests/components/Button.test.ts
```
