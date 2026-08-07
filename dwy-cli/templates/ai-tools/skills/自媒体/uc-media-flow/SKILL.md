---
name: uc-media-flow
description: |
  全流程编排：编号目录 PATHS、执行清单、stale、run_mode（fast|standard）；0080 工厂二选一。
  触发词：全流程、做一期、继续、media flow。
  入参：run_mode=fast|standard（可省略，省略则问用户）。
---

# uc-media-flow · 编排器

**契约：** [`CONTRACT.md`](./CONTRACT.md)  
**清单模板：** [`执行清单.template.md`](./执行清单.template.md)

## 行为（本 skill 内聚）

1. **先定模式再跑**：解析 `run_mode`，写入 `{work_dir}/执行清单.md`，再调度。  
2. **能自动的全部自动**（模式允许的连续段内）：建目录、维护清单、按 `next_stage` 调 skill。  
3. **产出可改终稿**：每步主文档；用户改文档或说继续即推进。  
4. **不确定不胡编**：硬停未满足不假装 done。  

---

## 参数：`run_mode`

| 值 | 含义 |
|----|------|
| **`fast`** | 连跑 **0010 product → 0020 topic → 0030 facts**；**事实产出后硬停** |
| **`standard`** | 每 skill 写完 → `ready_for_confirm` → 等人确认再下一步 |

解析：入参 → 清单 frontmatter → 开跑前问 A fast / B standard。

确认行：`run_mode=<值> · 本会话按此执行；改模式请说「改成 fast/standard」`

---

## 模式调度

### 共用

| 项 | 规则 |
|----|------|
| 步进 | `0010…0080` 与清单 `next_stage` |
| 硬停 | **0030 事实** · **0040 脚本** · **0050 design** · **0070 成片包** · **0080 工厂** · render |
| 改上游 | 下游 `stale` |

### `fast`

```text
while stage in {product, topic, facts}:
  跑 skill → 写主文档
  if facts: ready_for_confirm · 停
  else: done · 继续
确认 0030 后 → script，再按硬停表
```

旧 stage 名：`channel`/`position`/`brief` → **`product`**。

### `standard`

每步写完停；「确认并继续」才开下一步。

---

## 原则

1. 只维护 **`执行清单.md`**  
2. 新片：**`0010-product` … `0080-factory`**  
3. **0080** 工厂须用户选 remotion | hyperframe  

## Setup

```bash
mkdir -p "{work_dir}"/{0010-product,0020-topic,0030-facts,0040-script,0050-design,0060-assets/files,0070-package,0080-factory}
# 模板相对本 skill 包（sync 后：.claude/skills/uc-media-flow/ 或 .agents/skills/…）
cp -n 执行清单.template.md "{work_dir}/执行清单.md" 2>/dev/null || true
```

## 步进与主文档

| stage | skill | 主文档 |
|-------|--------|--------|
| product | uc-media-0010-product | `0010-product/产品卡-*.md` |
| topic | uc-media-0020-topic | `0020-topic/选题-*.md` |
| facts | uc-media-0030-facts | `0030-facts/事实-*.md`（作者技术资料库·可深） |
| script | uc-media-0040-script | `0040-script/脚本-*.md` |
| design | uc-media-0050-design | `0050-design/design-lock.md` |
| assets | uc-media-0060-assets | `0060-assets/素材清单.md` |
| package | uc-media-0070-package | `0070-package/成片包.md` + `shots.json` |
| factory | uc-media-0080-factory | `0080-factory/适配说明.md` + 工程 |

## 0080 调度

```text
validate shots.json
展示 design 工厂偏好
用户选 A Remotion | B HyperFrame
写 0080-factory/适配说明.md → 映射工程
```

## 硬停表

| 节点 | fast | standard |
|------|------|----------|
| 0010–0020 步间 | 不停 | 每步确认 |
| **0030 事实** | 批次终点 | 确认 |
| 0040 · 0050 · 0070 | 必确认 | 必确认 |
| 0060 等 | 可连续 | 每步确认 |
| **0080 选型** · render | 必确认 | 必确认 |

## 校验

```bash
# 校验脚本在兄弟 skill（sync 后与本 skill 同级）
python3 ../uc-media-0070-package/scripts/validate_shots.py \
  "{work_dir}/0070-package/shots.json"
```
