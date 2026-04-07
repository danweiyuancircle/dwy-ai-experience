# @danweiyuan/eui 测试用例清单

> 回测基准：58 个测试用例，5 个测试文件。版本变更后必须全部通过。
>
> 运行命令：`cd frontend/eui && pnpm vitest run`

---

## 1. cn 工具函数（7 个）

`src/utils/cn.test.ts`

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 合并 class 字符串 | `cn('foo', 'bar')` → `'foo bar'` |
| 2 | 条件 class（clsx 语法） | `false && 'hidden'` 被过滤，`true && 'visible'` 保留 |
| 3 | 数组输入 | `cn(['a', 'b'], 'c')` → `'a b c'` |
| 4 | 对象输入 | `{ 'text-red': true, 'text-blue': false }` → 只保留 true 的 key |
| 5 | Tailwind 冲突合并 | `cn('px-2', 'px-4')` → `'px-4'`，后者优先 |
| 6 | undefined/null 输入 | 自动忽略，只保留有效值 |
| 7 | 无参数调用 | 返回空字符串 |

---

## 2. EAlert 组件（14 个）

`src/components/alert/EAlert.test.ts`

### 渲染

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 渲染 role="alert" | 根元素具有 `role="alert"` 无障碍属性 |
| 2 | 渲染 title prop | 通过 `title` prop 传入标题文本，`[data-slot="alert-title"]` 显示对应内容 |
| 3 | 渲染 description prop | 通过 `description` prop 传入描述文本 |
| 4 | 默认插槽作为描述 | 默认 slot 内容渲染到 `[data-slot="alert-description"]` |
| 5 | title 插槽 | 通过 title slot 自定义标题内容 |
| 6 | 无标题时隐藏标题区域 | 未传 title prop 和 slot 时，`[data-slot="alert-title"]` 不渲染 |
| 7 | 无描述时隐藏描述区域 | 未传 description 和默认 slot 时，`[data-slot="alert-description"]` 不渲染 |
| 8 | data-slot 属性 | 根元素具有 `data-slot="alert"` |

### 变体

| # | 用例 | 测试要点 |
|---|------|---------|
| 9 | 默认变体样式 | 默认 variant 包含 `bg-card` class |
| 10 | destructive 变体样式 | `variant="destructive"` 包含 `text-destructive` class |

### 关闭按钮

| # | 用例 | 测试要点 |
|---|------|---------|
| 11 | 默认隐藏关闭按钮 | 未设置 `closable` 时无 button 元素 |
| 12 | closable 显示关闭按钮 | `closable=true` 时渲染 button，含 `aria-label="Close alert"` |
| 13 | 点击关闭触发 close 事件 | 点击关闭按钮后 emit `close` 事件 |

### 自定义

| # | 用例 | 测试要点 |
|---|------|---------|
| 14 | 合并自定义 class | 传入 `class="my-alert"` 后 class 列表包含 `my-alert` |

---

## 3. EBadge 组件（7 个）

`src/components/badge/EBadge.test.ts`

### 渲染

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 渲染插槽内容 | 默认 slot 文本正确显示 |
| 2 | 默认渲染为 div | 根元素标签为 `DIV`（Primitive 默认行为） |
| 3 | data-slot 属性 | 根元素具有 `data-slot="badge"` |

### 变体

| # | 用例 | 测试要点 |
|---|------|---------|
| 4 | 默认变体样式 | 默认 variant 包含 `bg-primary` class |
| 5 | secondary 变体样式 | `variant="secondary"` 包含 `bg-secondary` class |
| 6 | destructive 变体样式 | `variant="destructive"` 包含 `bg-destructive` class |
| 7 | outline 变体样式 | `variant="outline"` 包含 `text-foreground` class |

### 自定义

| # | 用例 | 测试要点 |
|---|------|---------|
| 8 | 合并自定义 class | 传入 `class="my-class"` 后 class 列表包含 `my-class` |

---

## 4. EButton 组件（12 个）

`src/components/button/EButton.test.ts`

### 渲染

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 默认渲染 button 元素 | 存在 `<button>`，slot 文本正确显示 |
| 2 | data-slot 隐含 | 通过 `find('button')` 定位 |

### 变体

| # | 用例 | 测试要点 |
|---|------|---------|
| 3 | 默认变体样式 | 默认 variant 包含 `bg-primary` class |
| 4 | destructive 变体样式 | `variant="destructive"` 包含 `bg-destructive` class |
| 5 | outline 变体样式 | `variant="outline"` 包含 `border` + `bg-background` class |

### 尺寸

| # | 用例 | 测试要点 |
|---|------|---------|
| 6 | sm 尺寸 | `size="sm"` 包含 `h-8` class |
| 7 | lg 尺寸 | `size="lg"` 包含 `h-10` class |

### 状态

| # | 用例 | 测试要点 |
|---|------|---------|
| 8 | disabled 禁用 | `disabled=true` 时具有 `disabled` 属性 |
| 9 | loading 加载中 | `loading=true` 时显示 SVG spinner 且自动 disabled |
| 10 | loading=false 无 spinner | `loading=false` 时不渲染 SVG |

### 交互

| # | 用例 | 测试要点 |
|---|------|---------|
| 11 | 点击事件 | 正常状态可点击，无 disabled 属性 |
| 12 | disabled 时不可点击 | disabled 状态点击后仍保持 disabled 属性 |

### 自定义

| # | 用例 | 测试要点 |
|---|------|---------|
| 13 | 合并自定义 class | 传入自定义 class 后同时保留变体 class（如 `bg-primary`） |

---

## 5. EInput 组件（21 个）

`src/components/input/EInput.test.ts`

### 渲染

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 渲染 input 元素 | 组件内存在 `<input>` |
| 2 | placeholder 属性 | `placeholder` prop 传递到 input 元素 |
| 3 | 默认 type 为 text | 未指定时 `type="text"` |
| 4 | maxlength 属性 | `maxlength` prop 传递到 input 元素 |
| 5 | data-slot 属性 | 根容器具有 `data-slot="input-root"` |

### 状态

| # | 用例 | 测试要点 |
|---|------|---------|
| 6 | disabled 禁用 | `disabled=true` 时 input 具有 disabled 属性 |
| 7 | readonly 只读 | `readonly=true` 时 input 具有 readonly 属性 |

### 尺寸

| # | 用例 | 测试要点 |
|---|------|---------|
| 8 | sm 尺寸 | `size="sm"` 时 input 包含 `h-8` class |
| 9 | lg 尺寸 | `size="lg"` 时 input 包含 `h-10` class |

### 事件

| # | 用例 | 测试要点 |
|---|------|---------|
| 10 | input 事件（v-model） | 输入文本后 emit `update:modelValue` 携带输入值 |
| 11 | blur 事件 | 失焦后 emit `blur` |
| 12 | focus 事件 | 聚焦后 emit `focus` |

### 清除功能

| # | 用例 | 测试要点 |
|---|------|---------|
| 13 | clearable 有值时显示清除按钮 | `clearable=true` + 有值时渲染 button |
| 14 | clearable 空值时隐藏清除按钮 | `clearable=true` + 空值时无 button |
| 15 | 点击清除 | 点击清除按钮后 emit `update:modelValue` 为空串 + emit `clear` |

### 密码切换

| # | 用例 | 测试要点 |
|---|------|---------|
| 16 | showPassword 显示切换按钮 | `showPassword=true` 时 input type 为 password 且有 toggle button |
| 17 | 切换密码可见性 | 点击 toggle 后 type 在 password/text 间切换 |
| 18 | 再次切换恢复隐藏 | 第二次点击后 type 恢复为 password |

### 安全属性

| # | 用例 | 测试要点 |
|---|------|---------|
| 19 | password 类型设置 autocomplete="off" | `type="password"` 时 input 有 `autocomplete="off"` |
| 20 | password 类型设置 spellcheck="false" | `type="password"` 时 input 有 `spellcheck="false"` |
| 21 | password 类型设置 autocorrect="off" | `type="password"` 时 input 有 `autocorrect="off"` |

---

## 6. escapeHtml 工具函数（7 个）

`tests/utils/escape.test.ts`

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 转义 & | `&` → `&amp;` |
| 2 | 转义 < > | `<script>` → `&lt;script&gt;` |
| 3 | 转义 " | `"` → `&quot;` |
| 4 | 转义 ' | `'` → `&#039;` |
| 5 | 组合转义 | `<img src="x" onerror='alert(1)'>` 全部转义 |
| 6 | 无特殊字符不变 | 普通文本原样返回 |
| 7 | 空字符串 | 返回空字符串 |

---

## 7. useNotification XSS 防护（4 个）

`tests/composables/useNotification.test.ts`

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 渲染通知标题 | title 正常显示 |
| 2 | 标题 XSS 防护 | `<img onerror=...>` 作为 title 时被转义为纯文本，不创建 img 元素 |
| 3 | 消息 XSS 防护 | `<script>` 作为 message 时被转义为纯文本，不创建 script 元素 |
| 4 | 不会双重转义 | `Hello & World` 正常显示 & 符号 |

---

## 8. useMessageBox XSS 防护（3 个）

`tests/composables/useMessageBox.test.ts`

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 标题 XSS 防护 | `<b>title</b>` 作为 title 时被转义为纯文本，不创建 b 元素 |
| 2 | 消息 XSS 防护 | `<script>` 作为 message 时被转义为纯文本，不创建 script 元素 |
| 3 | 按钮文字安全 | 默认按钮文字为"确定"/"取消" |

---

## 回测检查清单

```bash
# 1. 全量测试
cd frontend/eui && pnpm vitest run

# 2. 期望结果
# Test Files  91 passed (91)
# Tests       698 passed (698)

# 3. 单模块测试（调试用）
pnpm vitest run src/utils/cn.test.ts
pnpm vitest run src/components/alert
pnpm vitest run src/components/badge
pnpm vitest run src/components/button
pnpm vitest run src/components/input
```
