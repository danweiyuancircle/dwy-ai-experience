---
name: dwy-docs-check
description: "预览网站和文档完整性检查。触发条件：dwy-dev-qa 第 7 步、用户说'检查文档'、代码变更后准备提交时。"
---

# 文档完整性检查

检查预览网站全部 5 个模块的文档是否与源码一致，覆盖是否完整。发现问题自动修复，修复后重跑确认。

## 触发时机

- `dwy-dev-qa` 流程第 7 步自动调用
- 用户说"检查文档"/"文档是否最新"时手动触发
- 代码变更涉及源码目录时主动触发

## 7 项检查

### ① EUI 组件覆盖

**检查方法：**
```bash
# 取所有组件目录
ls frontend/eui/src/components/ | sort > /tmp/_eui_components.txt

# 取路由中的 EUI 页面
grep "path: '/eui/" frontend/playground/src/router.ts | sed "s/.*'\\/eui\\///" | sed "s/'.*//" | sort > /tmp/_eui_routes.txt

# 取导航配置中的 EUI 条目
grep "path: '/eui/" frontend/playground/src/data/nav-config.ts | sed "s/.*'\\/eui\\///" | sed "s/'.*//" | sort > /tmp/_eui_nav.txt

# 取搜索索引中的 EUI 条目
grep "path: '/eui/" frontend/playground/src/data/search-index.ts | sed "s/.*'\\/eui\\///" | sed "s/'.*//" | sort > /tmp/_eui_search.txt
```

**判定：** 每个组件目录应有对应的路由 + 导航条目 + 搜索条目。缺失任一项 = 不通过。

**修复：** 补充缺失的路由、导航配置、搜索索引条目，创建缺失的 demo 页面。

### ② EUI 组件一对一

**检查方法：** 扫描 `frontend/playground/src/views/*Demo.vue`，检查每个文件是否只展示一个组件。

**判定标准：**
- 一个文件对应一个组件 = 通过
- 语义强相关的组合（Alert+Badge、Tooltip+Popover、Dialog+Drawer、Checkbox+Radio）= 允许
- 不相关的组件混在一个文件 = 不通过

**修复：** 拆分为独立文件，更新路由和导航。

### ③ EUI API 表格准确性

**检查方法：** 抽查 10 个关键组件，读 `types.ts` 中的 Props/Emits interface 字段列表，对比 demo 页面中的 `propsData`/`eventsData`/`slotsData` 数组。

**抽查列表：** ESelect, ETable, EInput, EDialog, EDatePicker, EUpload, ETree, ETabs, EForm, EDropdown

**判定：** types.ts 中有的 prop/event 但 demo 页面的 API 表格没有 = 不通过。

**修复：** 补充缺失的 props/events/slots 到 demo 页面的数据数组。

### ④ Core 文档时效性

**检查方法：**
1. 读 `frontend/ekit/src/index.ts` 的所有导出函数/类型名
2. 对比 `claude-cli/templates/claude-global/skills/dwy-ekit/SKILL.md` 中列出的函数
3. 对比 `frontend/playground/src/views/core/` 下各文档页面的内容

**判定：** 源码导出了但 SKILL.md 或文档页没有 = 不通过。

**修复：** 更新 SKILL.md 对应模块段 + 文档页面。

### ⑤ Backend 文档时效性

**检查方法：**
1. 读 `backend/src/dwyeapi/` 下所有 `.py` 文件的 public 函数/类名
2. 对比 `claude-cli/templates/claude-global/skills/dwy-eapi/SKILL.md` 中列出的函数
3. 对比 `frontend/playground/src/views/backend/` 下各文档页面

**判定：** 源码有但文档没有 = 不通过。新增了 .py 模块但没有对应文档页 = 不通过。

**修复：** 更新 SKILL.md + 新建/更新文档页面 + 更新路由和导航。

### ⑥ CLI + Claude Code 时效性

**CLI 检查：**
1. 读 `claude-cli/bin/index.js` 的命令注册（command 列表）
2. 读 `claude-cli/src/sync.js` 的同步逻辑
3. 对比 `frontend/playground/src/views/cli/CreateDwyDoc.vue` 的内容

**Claude Code 检查：**
1. 列出 `claude-cli/templates/claude-global/skills/` 目录
2. 列出 `claude-cli/templates/claude-global/rules/` 目录
3. 列出 `claude-cli/templates/claude-global/hooks/` 目录
4. 对比 playground Claude Code 模块的导航配置是否包含所有条目
5. 验证 SkillDoc/RuleDoc/HookDoc 的 `import.meta.glob` 路径能匹配到所有文件

**判定：** 新增了 skill/rule/hook 但导航没更新 = 不通过。CLI 命令逻辑变了但文档没更新 = 不通过。

**修复：** 更新导航配置、文档页面内容。

### ⑦ 元数据一致性

**检查方法：**
```bash
# 路由总数
grep "path:" frontend/playground/src/router.ts | wc -l

# 导航条目总数（去重）
grep "path:" frontend/playground/src/data/nav-config.ts | wc -l

# 搜索索引条目数
grep "path:" frontend/playground/src/data/search-index.ts | wc -l
```

同时检查 `CLAUDE.md`：
- 组件数量是否与 `ls frontend/eui/src/components/ | wc -l` 一致
- 模块列表是否完整
- 构建/测试/发布命令是否与 `package.json` scripts 一致

**判定：** 路由数 >= 导航数 >= 搜索数，CLAUDE.md 数据与实际一致 = 通过。

**修复：** 补充缺失条目，修正 CLAUDE.md 中过时的数据。

## 输出格式

```
## 文档完整性检查报告

### ① EUI 组件覆盖 (X/Y)
- ✅ 全部覆盖 / ❌ 缺失：[列表]

### ② EUI 组件一对一
- ✅ 全部单组件 / ❌ 需拆分：[列表]

### ③ EUI API 表格 (抽查 10 个)
- ✅ 全部准确 / ❌ 过时：[列表]

### ④ Core 文档 (X/Y 模块)
- ✅ 全部一致 / ❌ 过时：[列表]

### ⑤ Backend 文档 (X/Y 模块)
- ✅ 全部一致 / ❌ 过时：[列表]

### ⑥ CLI + Claude Code
- ✅ 全部一致 / ❌ 过时：[列表]

### ⑦ 元数据一致性
- 路由 X | 导航 X | 搜索 X | CLAUDE.md ✅/❌

### 修复清单
1. [文件] — [动作]
```

## 自动修复流程

发现问题后：
1. 按修复清单逐项修复
2. 重跑对应检查项确认已修复
3. 全部通过后输出最终报告
