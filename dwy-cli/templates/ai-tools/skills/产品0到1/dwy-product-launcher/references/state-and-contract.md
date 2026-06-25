# 产品 0→1 流程 · 状态与产出契约（配套参考）

`dwy-product-launcher` 总控和各原子/阶段 skill 统一遵循本文件。

## 一、产出与缓存目录（最终全貌，**渐进式按需创建**）

下面是流程全部走完后的**目标结构**，不是初始化时一次建好的。**渐进式原则：每个阶段真正开始时，才创建它自己那一级目录和文件**——初始化只建项目根 + state.json，`01-立项/` 进立项才建，`02-需求规划/` 进需求阶段才建，以此类推。不要上来就把 01~05 五个阶段目录全建出来。

```
.dwy/prod/
  [项目名]/                  # 产品产出，入库（git 跟踪）
    01-立项/
      想法收敛.md           # dwy-explore：YC 6问逼清 + 收敛成结构化定义
      竞品分析.md
      需求市场验证.md         # 闸1·总闸门
      技术验证.md            # 闸2
      poc/                  # 最小 POC 代码
      MVP清单.md            # 闸3·≤7
    02-需求规划/
      PRD.md
      版本路线图.md
      开发任务拆解.md
    03-原型设计/
      wireframe/            # dwy-prototype 第一轮：低保真线框初稿（静态 HTML，一页一图）
      hifi/                 # dwy-prototype 第二轮：高保真平面图（静态 HTML，一页一图）
    04-架构设计/
      技术架构.md
      数据库设计.md          # 有后端时才出
      接口契约.md
    05-上线交付/
      验收报告.md
      上架物料.md
      埋点与指标.md
      下一版迭代规划.md
    09-开发日志.md
    state.json              # 进度 + 已确认结论，入库
```

**外部 skill 不在项目内**：pm-skills / superpowers 的副本装在**全局** `~/.dwy/skills/<name>/`（一台机一份、全项目共享），由 `dwy skills install` 维护，`dwy claude sync` 自检缺失时自动装。包装型原子 skill 运行时直接读这个全局路径，不在项目里缓存。

## 二、.gitignore 规则（总控初始化项目时写入）

产品产出 `.dwy/prod/[项目]/` **入库**（git 跟踪），无需任何忽略——外部 skill 在全局 `~/.dwy/skills/`，不落项目，没有要忽略的缓存。

注意：**不要**写整行 `.dwy/`（那会把产品文档也忽略）。本流程不需要在项目 `.gitignore` 加任何条目。

## 三、state.json schema

线性单向，只记进度 + 已确认结论，无回退状态机。

```json
{
  "schema_version": "3",
  "version": "1.0",
  "project_name": "...",
  "current_stage": 1,
  "current_round": "stage1_round1",
  "run_mode": "standard | auto",
  "confirmed": {
    "idea": { "mode": "startup | builder", "pass": true, "core_problem": "...", "target_user": "...", "value_prop": "...", "key_assumptions": [], "narrowest_wedge": "...", "boundaries": "..." },
    "competitors": {},
    "validation": { "pass": true, "evidence": "...", "method": "..." },
    "poc": { "pass": true, "deadlock": "...", "result": "..." },
    "mvp_features": [],
    "prd": {},
    "version_plan": {},
    "tasks": {},
    "wireframe": {},
    "prototype": {},
    "architecture": {},
    "dev_progress": { "<module>": { "<task>": "todo | done" } },
    "acceptance": {},
    "release": {}
  }
}
```

- `schema_version` — **state 结构版本**，当前 `"3"`，升级破坏性结构时 bump（迁移见第七节）。
- `version` — **产品版本**（用户 app 的 V1.0/V1.1 迭代号），与 schema_version 无关，别混。

字段名是各 skill 的对外契约，**回写方与读取方必须用同一名字**：

| 原子 skill | 回写字段 | 下游读取方 |
|---|---|---|
| dwy-explore | confirmed.idea（逼问理清 + 收敛成结构化定义） | dwy-competitor（target_user/wedge 定位）+ dwy-validate（core_problem/assumptions 转定量）+ dwy-mvp（wedge 砍范围）+ dwy-prd |
| dwy-competitor | confirmed.competitors | dwy-validate |
| dwy-validate | confirmed.validation | dwy-poc（仅 pass=true 才执行） |
| dwy-poc | confirmed.poc | dwy-mvp |
| dwy-mvp | confirmed.mvp_features | dwy-stage-prd |
| dwy-prd | confirmed.prd | dwy-version |
| dwy-version | confirmed.version_plan | dwy-tasks / dwy-stage-design |
| dwy-tasks | confirmed.tasks | dwy-stage-dev |
| dwy-prototype（第一轮·线框初稿） | confirmed.wireframe | dwy-prototype 第二轮（基于线框升保真） |
| dwy-prototype（第二轮·高保真平面图） | confirmed.prototype | dwy-architecture（原型定稿后才进架构） |
| dwy-architecture | confirmed.architecture | dwy-stage-dev |
| dwy-tdd-dev | confirmed.dev_progress | dwy-stage-ship |
| dwy-acceptance | confirmed.acceptance | dwy-release |
| dwy-release | confirmed.release | 迭代回到阶段二 |

## 四、外部 skill 全局安装 `~/.dwy/skills/`

包装型原子 skill（dwy-competitor / dwy-validate / dwy-mvp / dwy-prd / dwy-version / dwy-tasks / dwy-tdd-dev / dwy-acceptance / dwy-release）依赖 pm-skills / superpowers 的外部 skill，装在**全局** `~/.dwy/skills/<name>/`：

- 每个外部 skill 是**整个目录**（含 scripts/ 与配套 .md，不止 SKILL.md）
- 由 cli 命令 `dwy skills install` 安装/更新（clone 两仓库的指定 stable tag → 搬整目录 + LICENSE → 写 `VERSIONS.json`）
- `dwy claude sync` 自检：`~/.dwy/skills/` 缺失时自动装一次
- 当前 stable：pm-skills **v2.0.0** | superpowers **v6.0.3**（升级改 cli 的 `skills-install.js` 清单 tag）
- 原子 skill 运行时**只读** `~/.dwy/skills/<name>/`，缺失则提示用户先 `dwy skills install`，不自己拉、不降级

## 五、运行模式与流转（run_mode）

`state.json` 顶层 `run_mode`，取值 `standard | auto`，由 `dwy-explore` 在 idea 收敛后问一次写入（区别于 `confirmed.idea.mode` 的 startup/builder **产品类型**，`run_mode` 是**怎么跑**）。总控与每个 `dwy-stage-*` 都读它：

| run_mode | 阶段间 | stage 内门控（原型两轮 / PRD 确认等） | 硬闸门（validate 没人要 / poc 做不出 / 高风险不可逆） |
|---|---|---|---|
| `standard` | 每阶段准出后问「继续 / 停」 | 照常问用户 | 停 |
| `auto` | 不问，自动连跑到底出结果 | 全部 AI 自动决策、不问 | **仍停**（auto 不绕硬闸门） |

**流转规则**：每个 stage 准出 = 回写 `current_stage` + 按 `run_mode` 决定「问后流转」（standard）或「直接触发下一 `dwy-stage-*`」（auto）。总控 `dwy-product-launcher` 与单独触发某 stage **行为一致**，都走这套流转。最后一阶段 ship 无下游，正常结束。

**stage 独立触发 + 上游补齐**：单独触发某 `dwy-stage-*` 时上游 `confirmed.*` 缺失 → 不报错，基于已聊上下文 + 现有产出文件**轻量补齐**够本阶段用的上游结论，写回对应 `confirmed.*` 标注「上下文补齐」。**安全边界**：可补产出文档/范围类（prd/version_plan/tasks/prototype/architecture/mvp_features 范围）；**禁止**凭空标硬闸门 `pass=true`（`validation`/`poc` 只能由 launch 真实跑出）。

## 六、断点续跑

会话中断后，总控读 `state.json` 的 `current_stage` + `current_round`，从中断处续跑。已确认字段不重做。

## 七、schema 版本与迁移（单一来源）

**当前 `schema_version = "3"`。** 缺失或 `< 3` = 老结构，**读 state 的 skill（总控 / 任一 stage）必须先迁移再继续**——这是老用户无感升级的唯一入口。迁移**逐级叠加**（v1 项目走 v1→v2→v3）。新建项目直接写 `schema_version = "3"`。

### v1 → v2 迁移规则（AI 执行，幂等）
老 state（无 `schema_version`，或 dev_progress 是平层）按序处理：

1. **dev_progress 平层 → 嵌套**：`{"<module>": "todo|done"}` → `{"<module>": {"_legacy": "todo|done"}}`（旧模块整体视为一个已完成/待办任务占位；本版本新任务在该 module 下追加 `<task>`）
2. **旧 prototypes/ 原型归档**：`prototypes/` 目录下的旧原型文件 → 移到 `prototypes/wireframe/`，在该目录 `index` 注明「旧版原型（可交互白板），仅历史保留」；旧 `confirmed.prototype` **保留**，但标注「旧版产物，新两轮（线框 → 高保真平面图）可按需重跑」
3. **补 `confirmed.wireframe`**（若无）= 引用迁移后的 `prototypes/wireframe/`
4. **补顶层 `run_mode`**（若无）= `"standard"`
5. **写 `schema_version = "2"`**（继续走 v2→v3）
6. 迁移完在 `09-开发日志.md` 记一行（迁移前版本 / 改了什么）

### v2 → v3 迁移规则（AI 执行，幂等）
v2 把原型与架构拆成独立平级阶段目录、上线交付目录顺延。`schema_version = "2"`（或 v1→v2 刚处理完）的项目按序处理：

1. **原型目录独立**：`03-设计与架构/prototypes/wireframe|hifi/` → 移到 `03-原型设计/wireframe|hifi/`
2. **架构文档独立**：`03-设计与架构/{技术架构,数据库设计,接口契约}.md` → 移到 `04-架构设计/`
3. **上线交付顺延**：`04-上线交付/` 整体改名 `05-上线交付/`
4. 删空的 `03-设计与架构/`
5. **写 `schema_version = "3"`**
6. 迁移完在 `09-开发日志.md` 记一行

### 未来再升级
bump `schema_version` + 在本节追加 `vN → vN+1` 规则；**旧规则保留**，以支持跨多版本逐级迁移（v1→v2→v3→…）。
