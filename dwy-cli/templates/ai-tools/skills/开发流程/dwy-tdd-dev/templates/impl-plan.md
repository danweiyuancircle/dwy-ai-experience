---
status: in-progress    # in-progress | done
updated: <YYYY-MM-DD>
version: vN
---

# <版本名> 实施计划

> 假设执行者完全不懂这个代码库：每个 Task 写清动哪些文件、给出实际代码、确切命令 + 预期输出。DRY、YAGNI、TDD、频繁提交。每步是一个动作（2-5 分钟），用 `- [ ]` checkbox 跟踪。

**Goal**：<一句话，这个版本要建成什么>

**Architecture**：<2-3 句说清方案：模块怎么分、数据怎么流>

**Tech Stack**：<关键技术 / 库，对齐选定的技术方案>

---

## 示例 Task（填好的样板，照这个颗粒度写每个 Task）

### Task 1：笔记正文长度校验（前后端双层）

Files:
- Create: `src/validators/note.ts`
- Modify: `src/api/notes.ts:40-58`
- Test: `tests/validators/note.test.ts`

- [ ] **步骤 1：写失败测试**

```typescript
import { validateNoteBody } from '@/validators/note'

test('超过 5000 字的正文返回校验错误', () => {
  const body = 'a'.repeat(5001)
  const result = validateNoteBody(body)
  expect(result.ok).toBe(false)
  expect(result.error).toBe('正文最多 5000 字')
})

test('5000 字以内的正文通过', () => {
  const result = validateNoteBody('a'.repeat(5000))
  expect(result.ok).toBe(true)
})
```

- [ ] **步骤 2：运行看到失败**

Run: `pnpm vitest run tests/validators/note.test.ts`
Expected: FAIL —「validateNoteBody is not a function」（模块还没建）

- [ ] **步骤 3：最小实现**

```typescript
// src/validators/note.ts
const MAX_BODY = 5000

export function validateNoteBody(body: string): { ok: boolean; error?: string } {
  if (body.length > MAX_BODY) {
    return { ok: false, error: '正文最多 5000 字' }
  }
  return { ok: true }
}
```

- [ ] **步骤 4：运行看到通过**

Run: `pnpm vitest run tests/validators/note.test.ts`
Expected: PASS（2 passed），其它测试不受影响

- [ ] **步骤 5：commit（按 Git 提交规范：敏感扫描 + 规范 message + 禁 AI 署名）**

```bash
git add src/validators/note.ts tests/validators/note.test.ts
git commit -m "feat: 笔记正文 5000 字长度校验"
```

---

## 空白 Task 模板（每个真实 Task 复制一份填）

### Task N：<名称>

Files:
- Create: `<确切路径>`
- Modify: `<确切路径:起止行>`
- Test: `<确切测试路径>`

- [ ] **步骤 1：写失败测试**（贴实际测试代码，测真实行为）

```
<测试代码>
```

- [ ] **步骤 2：运行看到失败**

Run: `<确切测试命令>`
Expected: FAIL — <预期失败原因，必须是「功能没实现」>

- [ ] **步骤 3：最小实现**（只写让测试过的最小代码）

```
<实现代码>
```

- [ ] **步骤 4：运行看到通过**

Run: `<确切测试命令>`
Expected: PASS，其它测试不挂、输出无 warning

- [ ] **步骤 5：commit（按 Git 提交规范：敏感扫描 + 规范 message + 禁 AI 署名）**

```bash
git add <文件>
git commit -m "<type: 描述>"
```
