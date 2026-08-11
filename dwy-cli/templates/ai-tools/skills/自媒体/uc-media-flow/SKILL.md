---
name: uc-media-flow
description: |
  全流程：主题→0010（竞品+AI推荐演讲地图）→0030事实→0040脚本→制作轨；
  可选 0005/0090。触发词：全流程、做一期、继续、media flow、找选题。
---

# uc-media-flow · 编排器

**契约：** [`CONTRACT.md`](./CONTRACT.md)  
**清单：** [`执行清单.template.md`](./执行清单.template.md)

## 行为

1. 解析 `run_mode` → 写执行清单  
2. 频道闸门 → `channel-profile.md`（无则 0010 写）  
3. 主题：有则 skip 0005；无则 0005 停人选  
4. **0010 一次跑完**：竞品 + **AI 自动填演讲地图** → 再 0030…  
5. 改上游 → 下游 stale  

## 因果（强制）

```text
主题词 → 0010（竞品/差异化 + AI 推荐讲什么）→ 0030 按地图扩事实 → 0040 蒸馏
```

无独立「0020 产品」步——已并入 0010。

## `run_mode`

| 值 | 行为 |
|----|------|
| **fast** | 0010→0030 连跑后停；0040/0050 停；连 0060–0070；0080 停 |
| **standard** | 每步确认 |

### `fast` 伪码

```text
if 无主题: 0005 → 停
0010 竞品+推荐地图 → （不做则停）→ 0030 → 停
0040 → 停 → 0050 → 停 → 0060 → 0070 → 停 → 0080 → render
可选 0090
```

## Setup

```bash
mkdir -p "{project_root}/.dwy/uc-media"
mkdir -p "{work_dir}"/{0005-ideation,0010-product,0030-facts,0040-script,0050-design,0060-assets/files,0070-package,0080-factory}
cp -n 执行清单.template.md "{work_dir}/执行清单.md" 2>/dev/null || true
```

## 步进

| stage | skill | 主文档 |
|-------|--------|--------|
| channel | uc-media-0010-product | channel-profile.md |
| ideation | uc-media-0005-ideation | topic-backlog.md |
| **product** | **uc-media-0010-product** | **0010-product/产品卡-*.md** |
| facts | uc-media-0030-facts | 0030-facts/事实-*.md |
| script | uc-media-0040-script | 0040-script/脚本-*.md |
| design…factory | … | … |
| packaging | media-platform-packaging | 可选 |

## 硬停表

| 节点 | fast | standard |
|------|------|----------|
| 0005 | 无主题必停 | 停或 skip |
| 0010 | 连跑（不做则停） | 确认地图 |
| 0030 | 停 | 停 |
| 0040 · 0050 | 停 | 停 |
| 0060 | 连 | 停 |
| 0070 · 0080 | 停 | 停 |

## 校验

```bash
python3 ../uc-media-0070-package/scripts/validate_shots.py \
  "{work_dir}/0070-package/shots.json"
```
