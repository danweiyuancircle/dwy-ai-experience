# 产品 0→1 流程 · 状态与产出契约（配套参考）

`dwy-product-launcher` 总控和各原子/阶段 skill 统一遵循本文件。

## 一、产出与缓存目录

```
.dwy/prod/
  [项目名]/                  # 产品产出，入库（git 跟踪）
    01-立项/
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
  .cache/
    skills/                 # 外部 skill 缓存，gitignore 不入库
      manifest.json
      pm__<name>.md
      sp__<name>.md
```

## 二、.gitignore 规则（总控初始化项目时写入）

**部分入库部分忽略**：产出入库，缓存忽略。在项目 `.gitignore` 加：

```gitignore
# 产品 0→1 流程：产出入库，仅缓存忽略
.dwy/prod/.cache/
```

注意：不要写整行 `.dwy/`（那会把产品文档也忽略）。只忽略 `.dwy/prod/.cache/`。

## 三、state.json schema

线性单向，只记进度 + 已确认结论，无回退状态机。

```json
{
  "version": "1.0",
  "project_name": "...",
  "current_stage": 1,
  "current_round": "stage1_round1",
  "confirmed": {
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

## 四、外部 skill 缓存 manifest.json

```json
{
  "version": "1.0",
  "skills": {
    "pm/competitor-analysis": {
      "repo": "phuryn/pm-skills",
      "release_tag": "v2.0.0",
      "fetched_at": "2026-06-24",
      "local": "pm__competitor-analysis.md"
    }
  }
}
```

当前 stable：pm-skills **v2.0.0** | superpowers **v6.0.3**。
`dwy-skills-update` 比对最新 stable release（跳过 prerelease/beta/rc/含 `-` 的 tag）更新。

## 五、断点续跑

会话中断后，总控读 `state.json` 的 `current_stage` + `current_round`，从中断处续跑。已确认字段不重做。
