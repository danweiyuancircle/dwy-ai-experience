---
name: uc-media-0080-factory
description: |
  工厂适配（0080）：package 冻结后，由用户选择 Remotion 或 HyperFrame 生成/映射工程。
  触发词：Remotion、HyperFrame、工厂、适配、出片工程、0080。
  不要用于：改口播语义、改事实、当 flow。
---

# uc-media-0080-factory · 工厂适配

> **可单独执行。** 上游须有合法 `0070-package/shots.json`。

**上游 schema：** [`../uc-media-0070-package/shots.schema.json`](../uc-media-0070-package/shots.schema.json)

## 行为（本 skill 内聚）

1. validate package；读 design 偏好；**选型确认后**映射/脚手架、写 `适配说明.md`。  
2. **工厂未确认 → 停，不写工程**。  
3. 不发明镜号、不私自改 vo/秒。  

---

## 大步骤契约

| 项 | 内容 |
|----|------|
| **序** | 0080 |
| **stage** | `factory` |
| **上游** | `0070-package/shots.json` validate OK |
| **主文档** | **`0080-factory/适配说明.md`** |
| **工程目录** | `{episode_dir}/remotion/` **或** `hyperframe/` |
| **禁止** | 静默替用户选定工厂 |

## 0. 用户选择工厂（硬停）

| 选项 | 工程根 |
|------|--------|
| **A. Remotion** | `{episode_dir}/remotion/` |
| **B. HyperFrame** | `{episode_dir}/hyperframe/` |

## 1. 校验

```bash
# 校验脚本在兄弟 skill（sync 后与本 skill 同级）
python3 ../uc-media-0070-package/scripts/validate_shots.py \
  "{work_dir}/0070-package/shots.json"
```

失败 → 回 0070。

## 2. 适配说明.md

选型 · 上游路径 · 校验 · 工程根 · 镜号映射 · 已做/未做 ·「改口播回 0040/0070」

## 3A/3B

Remotion：同号映射 · frames · durations/catalog  
HyperFrame：按模板映射；无模板列缺口  
