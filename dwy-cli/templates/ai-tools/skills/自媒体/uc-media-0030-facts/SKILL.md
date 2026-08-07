---
name: uc-media-0030-facts
description: |
  事实资料库（0030）：多源深检索汇聚技术笔记（可深、可发散）；必出 事实-*.md + sources.json + index.html（悬停溯源）。
  触发词：事实、资料库、学习笔记、原理深挖、资料汇聚、事实网页、0030。
  不要用于：口播/分镜（→0040）；选题竞品（→0020）；产品定义（→0010）。
---

# uc-media-0030-facts · 事实资料库（作者学习 + 网页）

**目标读者：你（技术作者）——先看懂。** 不是观众口播干粮。

| 要 | 不要 |
|----|------|
| 多源权威检索、写细写透、关键图 | 空心一句话提纲 |
| 相对 0010 **可发散**（为理解主线） | 无关百科（整本 Agent/MCP） |
| 文内 `[[cite:Sn]]` + **必出网页** 悬停看出处 | 编造 URL；只给无出处断言 |
| 公式/伪代码/争议并列 | 按镜号拆口播硬句 |

**必交付：**

| 文件 | 说明 |
|------|------|
| `0030-facts/事实-{主题}.md` | 人读深库 |
| `0030-facts/sources.json` | 结构化来源（悬停数据） |
| `0030-facts/index.html` | **只渲染事实**；引用悬停：网站·权威性·URL |
| `0030-facts/images/` | 可选；图尽量镜像，失败则外链+出处 |

**模板：** [`templates/事实资料库.template.md`](./templates/事实资料库.template.md)  
**网页构建：**

```bash
# 脚本相对本 skill 包（sync 后：.claude/skills/uc-media-0030-facts/ 或 .agents/skills/…）
python3 scripts/build_facts_html.py \
  --md "{work_dir}/0030-facts/事实-{主题}.md" \
  --sources "{work_dir}/0030-facts/sources.json" \
  --out "{work_dir}/0030-facts/index.html"
```

---

## 行为

1. **上游** `0010-product` = 议题起点（非深度天花板）；`0020-topic` 可选补误区。  
2. **拆 3–7+ 学习角度** → **并行**多源检索（P0 论文/官方优先）→ 写深 MD。  
3. **发散规则**：允许 tokenization、causal mask、KL、DPO 等帮助理解主线的前置；禁止跑题产品线。  
4. **深度门槛**：每角度 = 定义→步骤→例子/公式→边界→≥2 源；关键机制 **≥1 图**（可溯源）。  
5. **引用**：正文 `[[cite:S1]]` 或 `[[cite:S1,S2]]`；`sources.json` 含 id/title/url/site/authority/authority_label_zh。  
6. **权威性枚举：** `primary_official` · `primary_academic` · `secondary_edu` · `secondary_tech` · `media`。  
7. **必生成 index.html**；成片裁切备忘进 MD 即可，网页默认折叠。  
8. **禁止**主交付口播硬句/镜号表。

---

## 大步骤契约

| 项 | 内容 |
|----|------|
| **序** | 0030 |
| **目录** | `{work_dir}/0030-facts/` |
| **主文档** | `事实-{主题}.md` |
| **机读** | `sources.json` |
| **网页** | `index.html`（必出） |
| **下游** | 0040 读 MD 蒸馏；不依赖 HTML |

---

## 质量自检

- [ ] 明显细于「通识提纲」；可含公式/分步  
- [ ] 可发散但仍服务「看懂主题」  
- [ ] 关键图有出处  
- [ ] cite 与 sources.json 一致  
- [ ] 打开 index.html 悬停可见网站/权威性/URL  
- [ ] 网页无流水线/口播噪音  
