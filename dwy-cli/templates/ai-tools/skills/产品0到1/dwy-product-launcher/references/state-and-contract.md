# 产品 0→1 流程 · 状态与产出契约（配套参考）

`dwy-product-launcher` 总控和各原子/阶段 skill 统一遵循本文件。

## 一、产出与缓存目录（最终全貌，**渐进式按需创建**）

下面是流程全部走完后的**目标结构**，不是初始化时一次建好的。**渐进式原则：每个阶段真正开始时，才创建它自己那一级目录和文件**——初始化只建项目根 + state.json，`01-立项/` 进立项才建，`02-需求规划/` 进需求阶段才建，以此类推。不要上来就把 01~04 四个阶段目录全建出来。

```
.dwy/prod/
  [项目名]/                  # 产品产出，入库（git 跟踪）
    01-立项/
      想法探索.md           # dwy-explore：YC 6问逼清方向
      想法收敛.md
      竞品分析.md
      需求市场验证.md         # 闸1·总闸门
      技术验证.md            # 闸2
      poc/                  # 最小 POC 代码
      MVP清单.md            # 闸3·≤7
    02-需求规划/
      PRD.md
      版本路线图.md
      开发任务拆解.md
    03-设计与架构/
      prototypes/           # dwy-whiteboard-prototype 白板 HTML
      技术架构.md
      数据库设计.md
      接口契约.md
    04-上线交付/
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
  "version": "1.0",
  "project_name": "...",
  "current_stage": 1,
  "current_round": "stage1_round1",
  "confirmed": {
    "exploration": { "mode": "startup | builder", "direction": "...", "pass": true },
    "idea": {},
    "competitors": {},
    "validation": { "pass": true, "evidence": "...", "method": "..." },
    "poc": { "pass": true, "deadlock": "...", "result": "..." },
    "mvp_features": [],
    "prd": {},
    "version_plan": {},
    "tasks": {},
    "prototype": {},
    "architecture": {},
    "dev_progress": { "<module>": "todo | done" },
    "acceptance": {},
    "release": {}
  }
}
```

字段名是各 skill 的对外契约，**回写方与读取方必须用同一名字**：

| 原子 skill | 回写字段 | 下游读取方 |
|---|---|---|
| dwy-explore | confirmed.exploration | dwy-ideate（收敛）+ dwy-competitor（Q3/Q4 定位）+ dwy-validate（Q1/Q2 转定量）+ dwy-mvp（Q4 砍范围） |
| dwy-ideate | confirmed.idea | dwy-competitor |
| dwy-competitor | confirmed.competitors | dwy-validate |
| dwy-validate | confirmed.validation | dwy-poc（仅 pass=true 才执行） |
| dwy-poc | confirmed.poc | dwy-mvp |
| dwy-mvp | confirmed.mvp_features | dwy-stage-prd |
| dwy-prd | confirmed.prd | dwy-version |
| dwy-version | confirmed.version_plan | dwy-tasks / dwy-stage-design |
| dwy-tasks | confirmed.tasks | dwy-stage-dev |
| dwy-prototype | confirmed.prototype | — |
| dwy-architecture | confirmed.architecture | dwy-stage-dev |
| dwy-tdd-dev | confirmed.dev_progress | dwy-stage-ship |
| dwy-acceptance | confirmed.acceptance | dwy-release |
| dwy-release | confirmed.release | 迭代回到阶段二 |

## 四、外部 skill 全局安装 `~/.dwy/skills/`

包装型原子 skill（dwy-ideate / dwy-competitor / dwy-validate / dwy-mvp / dwy-prd / dwy-version / dwy-tasks / dwy-tdd-dev / dwy-acceptance / dwy-release）依赖 pm-skills / superpowers 的外部 skill，装在**全局** `~/.dwy/skills/<name>/`：

- 每个外部 skill 是**整个目录**（含 scripts/ 与配套 .md，不止 SKILL.md）
- 由 cli 命令 `dwy skills install` 安装/更新（clone 两仓库的指定 stable tag → 搬整目录 + LICENSE → 写 `VERSIONS.json`）
- `dwy claude sync` 自检：`~/.dwy/skills/` 缺失时自动装一次
- 当前 stable：pm-skills **v2.0.0** | superpowers **v6.0.3**（升级改 cli 的 `skills-install.js` 清单 tag）
- 原子 skill 运行时**只读** `~/.dwy/skills/<name>/`，缺失则提示用户先 `dwy skills install`，不自己拉、不降级

## 五、断点续跑

会话中断后，总控读 `state.json` 的 `current_stage` + `current_round`，从中断处续跑。已确认字段不重做。
