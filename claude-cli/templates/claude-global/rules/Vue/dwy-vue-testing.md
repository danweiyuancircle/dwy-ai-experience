---
description: Vue Vitest 测试规范（目录组织、技术栈、AAA 结构、打包隔离）
paths:
  - "**/*.test.ts"
  - "**/*.spec.ts"
  - "**/tests/**/*.ts"
---

# Vue Vitest 测试规范

适用于 Vue 3 + Vitest + @vue/test-utils + happy-dom 项目。

---

## 一、测试目录组织（强制）

### 核心约束

**测试目录与业务源码（`src/`）并列、独立存放。** 测试文件**禁止**混入 `src/`。

### 强制规则

- 测试根目录固定为 `tests/`，与 `src/` 平级
- **禁止**在 `src/` 中放任何 `*.test.ts` / `*.spec.ts` / `__tests__/` 文件
- 测试目录内部结构**镜像**源码业务聚合结构（见 `dwy-vue-core` rule 第一节）
- 测试文件命名：`*.test.ts`（vitest 默认发现规则）
- 测试函数命名：描述行为而非实现
- `vitest.config.ts` **独立文件**，不与 `vite.config.ts` 合并；显式声明 `test.include`
- `tsconfig.app.json` 的 `include` **只包含 `src/`**，**禁止**包含 `tests/`，确保打包不携带测试代码
- 测试相关依赖（`vitest` / `@vue/test-utils` / `happy-dom` 等）放 `devDependencies`，**禁止**进生产依赖
- 测试文件中通过 `@` 别名导入源码，**禁止**用 `../../../src/` 相对路径回溯

### 标准目录结构（参考）

```
project/
├── src/
│   ├── modules/
│   │   ├── users/
│   │   │   ├── api.ts
│   │   │   ├── store.ts
│   │   │   ├── views/UserListView.vue
│   │   │   └── components/UserCard.vue
│   │   └── orders/
│   ├── shared/
│   └── core/
├── tests/                          # 测试根目录（与 src/ 并列）
│   ├── modules/
│   │   ├── users/
│   │   │   ├── api.test.ts
│   │   │   ├── store.test.ts
│   │   │   └── UserCard.test.ts
│   │   └── orders/
│   └── shared/
├── vitest.config.ts
├── tsconfig.app.json               # include 只含 src/
└── package.json
```

> 具体目录布局由项目结构决定（单包、monorepo 子包、扁平 `src/views/` 等），AI 自行判断；唯一不变的是"测试目录独立、与源码并列"。

---

## 二、技术栈

- **Vitest** + **@vue/test-utils** + **happy-dom**
- 测试 API 请求时用 Vitest 内置 mock 或 `msw`，**禁止**真发起网络

```bash
pnpm add -D vitest @vue/test-utils happy-dom
```

### vitest.config.ts

```typescript
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  test: {
    environment: 'happy-dom',
    include: ['tests/**/*.test.ts'],
  },
})
```

### tsconfig.app.json

```json
{
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"]
}
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

---

## 三、测试编写规范

### 强制规则

- 测试结构遵循 **Arrange-Act-Assert**
- 一个测试只验证**一个行为**，**禁止**一个 test 函数堆多个不相关断言
- 断言必须具体（字段值），**禁止**只断言"不报错"
- 必须覆盖：成功路径、失败路径、边界值
- 测试中**必须**用 `@` 别名导入源码

```typescript
// tests/modules/users/store.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/modules/users/store'

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('isLoggedIn 在 token 为 null 时返回 false', () => {
    // Arrange
    const store = useAuthStore()

    // Act + Assert
    expect(store.isLoggedIn).toBe(false)
  })

  it('logout 后清空 token 与 user', () => {
    const store = useAuthStore()
    store.$patch({ token: 'abc', user: { uuid: 'u1' } as any })

    store.logout()

    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
  })
})
```

---

## 四、违规检测清单

| 检查项 | 违规模式 | 严重程度 |
|--------|---------|---------|
| 测试与源码混放 | 测试文件放 `src/` 内（`src/utils/format.test.ts` / `src/**/__tests__/`） | 高 |
| 打包污染 | `tsconfig.app.json` 的 `include` 包含 `tests/` | 高 |
| 相对路径回溯 | 测试中 `import ... from '../../../src/...'` 而非 `@/` 别名 | 中 |
| 测试目录不规范 | 项目无独立 `tests/` 目录或 `vitest.config.ts` 未显式声明 `include` | 高 |
| 测试无断言 | 只调用接口不断言响应字段 | 高 |
| 测试依赖泄漏 | `vitest` / `@vue/test-utils` 等出现在 `dependencies` | 高 |
| 真发起网络 | 测试中直接调真实后端 API，未 mock | 高 |
| 测试镜像断裂 | 测试目录结构与 `src/` 业务聚合结构不对应，难以定位 | 中 |
