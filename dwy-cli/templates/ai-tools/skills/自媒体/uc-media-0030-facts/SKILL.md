---
name: uc-media-0030-facts
description: |
  事实资料库（0030）：按 0010 产品卡演讲地图（内容柱）扩展深检索；
  必出 事实-*.md + sources.json + index.html。
  触发词：事实、资料库、原理深挖、0030。
  不要用于：口播（→0040）；竞品/地图（→0010）。
---

# uc-media-0030-facts · 事实资料库

**目标读者：作者——先看懂。** 不是口播干粮。

**扩展起点：0010 产品卡 §3 演讲地图（内容柱）**——按「讲什么」扩深；可深于成片「不讲」。

| 要 | 不要 |
|----|------|
| 多源权威、写细写透、关键图 | 空心提纲 |
| 相对 **0010 内容柱** 可发散 | 无视产品卡乱挖 |
| `[[cite:Sn]]` + index.html 悬停出处 | 编 URL |
| 公式/伪代码/争议并列 | 镜号口播 |

**必交付：** `事实-*.md` · `sources.json` · `index.html` · 可选 `images/`

**模板：** [`templates/事实资料库.template.md`](./templates/事实资料库.template.md)

```bash
python3 scripts/build_facts_html.py \
  --md "{work_dir}/0030-facts/事实-{主题}.md" \
  --sources "{work_dir}/0030-facts/sources.json" \
  --out "{work_dir}/0030-facts/index.html"
```

---

## 行为

1. **上游硬依赖** `0010-product/产品卡-*.md` 的 **§3 讲什么/不讲/分块**（兼容旧路径见 CONTRACT）。  
2. 按内容柱拆 3–7+ 学习角度 → 并行检索 → 写深 MD。  
3. 发散须服务内容柱主线。  
4. 每角度：定义→步骤→例子/公式→边界→≥2 源；关键机制 ≥1 图。  
5. cite 与 sources.json 一致；权威性枚举同前。  
6. 必生成 index.html。  
7. 禁止主交付口播/镜号表。

---

## 契约

| 项 | 内容 |
|----|------|
| **序** | 0030 |
| **目录** | `{work_dir}/0030-facts/` |
| **上游** | **0010 产品卡演讲地图** |
| **下游** | 0040 按 0010 地图蒸馏 |

## 质量自检

- [ ] 已 read 0010 §3 内容柱并按柱扩展  
- [ ] 细于通识提纲；cite 一致；index 可悬停  
