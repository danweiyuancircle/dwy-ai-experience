# dwy skills 第三方编排 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 `dwy skills`，用全局收藏清单 + 官方命令编排第三方 skills/plugins 的安装、更新、卸载，并支持 export/import 换机。

**Architecture:** dwy 只做编排层。`skills-catalog.js` 管 `~/.dwy/skills-catalog/catalog.json`；`skills-install.js` 生成并执行 `npx skills` / `claude plugin` 命令；`skills-scan.js` 扫描本机已装并标注来源；`skills-cmd.js` 接交互与子命令；不改 `dwy sync`。

**Tech Stack:** Node ESM、fs-extra、node:test、现有 clack/searchable UI、child_process 可注入 runner。

**Spec:** `docs/superpowers/specs/2026-11-24-dwy-skills-catalog-design.md`

## Global Constraints

- 确认前不执行安装/卸载
- 不自建下载器；只调官方命令
- catalog 不存绝对路径与凭据
- dwy 模板 skills 只读，remove 拒绝
- `dwy --help` / `CLAUDE.md` / `dwy-cli/CHANGELOG.md` 同步；旧帮助测试里 `doesNotMatch(/dwy skills/)` 必须改为正向断言

---

### Task 1: Catalog CRUD + export/import

**Files:**
- Create: `dwy-cli/src/skills-catalog.js`
- Test: `dwy-cli/tests/skills-catalog.test.js`

**Interfaces:**
- Produces: `catalogPath(homeDir)`, `loadCatalog(homeDir)`, `saveCatalog(homeDir, catalog)`, `addCatalogEntry(homeDir, entry)`, `removeCatalogEntry(homeDir, id)`, `exportCatalog(homeDir, file)`, `importCatalog(homeDir, file, { merge })`, `normalizeEntry(raw)`

- [ ] **Step 1: Write failing tests for load/add/remove/export/import**

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import {
  loadCatalog, addCatalogEntry, removeCatalogEntry,
  exportCatalog, importCatalog, catalogPath,
} from '../src/skills-catalog.js'

async function tempHome() {
  return fs.mkdtemp(path.join(os.tmpdir(), 'dwy-skills-catalog-'))
}

test('empty home loads versioned empty catalog', async () => {
  const home = await tempHome()
  const catalog = await loadCatalog(home)
  assert.equal(catalog.version, 1)
  assert.deepEqual(catalog.entries, [])
})

test('add upserts by id and export/import roundtrip', async () => {
  const home = await tempHome()
  await addCatalogEntry(home, {
    kind: 'skills-cli',
    source: 'vercel-labs/agent-skills',
    skills: ['react-best-practices'],
    agents: ['claude-code'],
  })
  await addCatalogEntry(home, {
    kind: 'skills-cli',
    source: 'vercel-labs/agent-skills',
    skills: ['react-best-practices', 'web-design'],
    agents: ['claude-code', 'codex'],
  })
  let catalog = await loadCatalog(home)
  assert.equal(catalog.entries.length, 1)
  assert.deepEqual(catalog.entries[0].skills, ['react-best-practices', 'web-design'])

  const out = path.join(home, 'exported.json')
  await exportCatalog(home, out)
  const home2 = await tempHome()
  await importCatalog(home2, out)
  catalog = await loadCatalog(home2)
  assert.equal(catalog.entries[0].source, 'vercel-labs/agent-skills')

  await removeCatalogEntry(home2, catalog.entries[0].id)
  assert.equal((await loadCatalog(home2)).entries.length, 0)
  assert.equal(catalogPath(home), path.join(home, '.dwy', 'skills-catalog', 'catalog.json'))
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd dwy-cli && node --test tests/skills-catalog.test.js`
Expected: FAIL module not found

- [ ] **Step 3: Implement catalog module**

实现要点：`normalizeEntry` 校验 kind∈{skills-cli,claude-plugin,claude-marketplace}；缺 id 时用 source；拒绝绝对路径字段；`import` 默认 merge（同 id 覆盖）。

- [ ] **Step 4: Run tests PASS**

Run: `cd dwy-cli && node --test tests/skills-catalog.test.js`

- [ ] **Step 5: Commit**

```bash
git add dwy-cli/src/skills-catalog.js dwy-cli/tests/skills-catalog.test.js docs/superpowers/specs/2026-11-24-dwy-skills-catalog-design.md docs/superpowers/plans/2026-11-24-dwy-skills-catalog.md
git commit -m "$(cat <<'EOF'
feat(cli): add third-party skills catalog storage

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Official command builders + runner

**Files:**
- Create: `dwy-cli/src/skills-install.js`
- Test: `dwy-cli/tests/skills-install.test.js`

**Interfaces:**
- Consumes: catalog entry shape from Task 1
- Produces: `buildInstallCommand(entry)`, `buildUpdateCommand(entry)`, `buildRemoveCommand(target)`, `runCommands(commands, { runCommand, confirm })` → `{ ok, failed }`

- [ ] **Step 1: Failing tests for command generation**

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import { buildInstallCommand, buildUpdateCommand, buildRemoveCommand, runCommands } from '../src/skills-install.js'

test('skills-cli install maps to npx skills add -g', () => {
  const cmd = buildInstallCommand({
    kind: 'skills-cli',
    source: 'vercel-labs/agent-skills',
    skills: ['web-design'],
    agents: ['claude-code', 'codex'],
  })
  assert.deepEqual(cmd, {
    cmd: 'npx',
    args: ['skills', 'add', 'vercel-labs/agent-skills', '-g', '-a', 'claude-code,codex', '-s', 'web-design', '-y'],
    label: 'skills-cli: vercel-labs/agent-skills',
  })
})

test('claude-plugin install/update/remove', () => {
  assert.deepEqual(buildInstallCommand({ kind: 'claude-plugin', source: 'feature-dev@claude-plugins-official' }).args,
    ['plugin', 'install', 'feature-dev@claude-plugins-official'])
  assert.equal(buildInstallCommand({ kind: 'claude-plugin', source: 'x' }).cmd, 'claude')
  assert.deepEqual(buildUpdateCommand({ kind: 'claude-plugin', source: 'feature-dev@claude-plugins-official' }).args,
    ['plugin', 'update', 'feature-dev@claude-plugins-official'])
  assert.deepEqual(buildRemoveCommand({ kind: 'claude-plugin', source: 'feature-dev@claude-plugins-official' }).args,
    ['plugin', 'uninstall', 'feature-dev@claude-plugins-official'])
})

test('runCommands continues after failure and summarizes', async () => {
  const calls = []
  const result = await runCommands([
    { cmd: 'a', args: ['1'], label: 'one' },
    { cmd: 'b', args: ['2'], label: 'two' },
  ], {
    runCommand: async (cmd, args) => {
      calls.push([cmd, ...args])
      if (cmd === 'a') throw new Error('boom')
    },
  })
  assert.deepEqual(calls, [['a', '1'], ['b', '2']])
  assert.equal(result.ok.length, 1)
  assert.equal(result.failed.length, 1)
  assert.match(result.failed[0].error, /boom/)
})
```

- [ ] **Step 2: Run FAIL**

Run: `cd dwy-cli && node --test tests/skills-install.test.js`

- [ ] **Step 3: Implement builders + injectable runner**

`claude-marketplace` → `claude plugin marketplace add|update|remove`。skills-cli remove 用 `npx skills remove -g -y <names>`。默认 agents 缺省时 `-a` 不传或传 `*` 需在实现里选一种并写进测试：缺省不传 `-a`，让官方用其默认。

- [ ] **Step 4: PASS + Commit**

```bash
git add dwy-cli/src/skills-install.js dwy-cli/tests/skills-install.test.js
git commit -m "$(cat <<'EOF'
feat(cli): build official skills/plugin install commands

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Installed scan + provenance

**Files:**
- Create: `dwy-cli/src/skills-scan.js`
- Test: `dwy-cli/tests/skills-scan.test.js`

**Interfaces:**
- Consumes: `loadCatalog`, `GLOBAL_SKILL_DIR_SEGMENTS` / `resolveGlobalSkillDir`
- Produces: `scanInstalledSkills({ homeDir, codexHome, templateSkillNames, catalog, listPlugins })` → `{ skills, plugins }`

- [ ] **Step 1: Failing tests with fake home dirs + fake plugin list**

覆盖：目录 skill 发现、catalog 命中、`dwy-template` 标注、unknown。

- [ ] **Step 2: Implement scan**

插件列表通过注入 `listPlugins()`（默认跑 `claude plugin list` 文本解析，至少识别 `name@marketplace` 行）。

- [ ] **Step 3: PASS + Commit**

---

### Task 4: CLI routing, help, non-interactive subcommands

**Files:**
- Create: `dwy-cli/src/skills-cmd.js`
- Modify: `dwy-cli/bin/index.js`
- Modify: `dwy-cli/src/cli-help.js`
- Modify: `dwy-cli/tests/cli-help.test.js`（`doesNotMatch(/dwy skills/)` → 正向匹配）
- Test: `dwy-cli/tests/skills-cmd.test.js`
- Modify: `CLAUDE.md` 命令列表、`dwy-cli/CHANGELOG.md`

**Interfaces:**
- Produces: `runSkillsCommand(argv, deps)` 处理 `list|catalog|add|install|update|remove` 与无参交互入口（交互可先 stub 为提示用子命令，Task 5 补全）

- [ ] **Step 1: Help + catalog list/add/export 的非交互测试**
- [ ] **Step 2: 接 bin 路由：`argv[0]==='skills'` → `runSkillsCommand(argv.slice(1))`**
- [ ] **Step 3: 更新帮助与文档；模板 skill remove 拒绝**
- [ ] **Step 4: PASS + Commit**

---

### Task 5: Interactive `dwy skills` flow

**Files:**
- Modify: `dwy-cli/src/skills-cmd.js`
- Test: `dwy-cli/tests/skills-cmd.test.js`（注入 prompts，断言预览命令与确认取消无副作用）

- [ ] **Step 1: 操作选择 → 多选 → agents → 预览 → 确认 → runCommands**
- [ ] **Step 2: 取消确认路径零调用 runner**
- [ ] **Step 3: PASS + Commit**

---

## Spec coverage check

- 命令面 / catalog / 扫描 / 官方路由 / export-import / 边界 / 验收 → Tasks 1–5
- 不做云同步、不改 sync、不自建下载器 → 全局约束，无任务违背
