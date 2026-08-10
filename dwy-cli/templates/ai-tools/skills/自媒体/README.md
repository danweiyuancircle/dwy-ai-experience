# 自媒体 skills（uc-media）

短视频 / 科普自媒体全流程 Agent skill 包。源迁入自 `xiaoyuan-knowledge-town/function-tools/skills`，由 dwy 统一管理；`dwy` 交互同步可选本分类。

每 skill 自包含、可单独跑；**编号目录 + 每步一份主文档**。

## 工作目录结构（media 根）

```text
media/
  执行清单.md
  0010-product/        产品卡-*.md     ← 群体·主题·分发·讲/不讲·分块时长
  0020-topic/          选题-*.md       ← 多源竞品 + 差异化讲法
  0030-facts/          事实-*.md
  0040-script/         脚本-*.md
  0050-design/         design-lock.md
  0060-assets/         素材清单.md · files/
  0070-package/        成片包.md · shots.json
  0080-factory/        适配说明.md     ← 用户选 remotion | hyperframe
```

工程在 episode 根：`remotion/` 或 `hyperframe/`。

## Skills

| Skill | 主文档 |
|-------|--------|
| **uc-media-flow** | 执行清单.md（`fast` 到 0030 事实停 · `standard` 逐步确认） |
| **uc-media-0010-product** | `0010-product/产品卡-*.md` |
| **uc-media-0020-topic** | `0020-topic/选题-*.md`（竞品表 + 差异化） |
| uc-media-0030-facts | `事实-*.md` + `sources.json` + **`index.html`**（深库·图·悬停出处） |
| uc-media-0040-script | `0040-script/脚本-*.md` |
| uc-media-0050-design | `0050-design/design-lock.md` |
| uc-media-0060-assets | `0060-assets/素材清单.md` |
| uc-media-0070-package | 成片包.md + shots.json |
| **uc-media-0080-factory** | 适配说明.md（必选工厂） |
| uc-media-comic-kit | 漫画科普表达规范（0050/0060 风格扩展） |
| uc-media-knowledge-town | 知识小城频道视觉 / Remotion 预设 |
| **media-platform-packaging** | 多平台包装（B站/抖音/小红书标题简介标签 + 16:9/4:3/3:4 封面） |

契约：[`uc-media-flow/CONTRACT.md`](./uc-media-flow/CONTRACT.md)

## 路径约定（dwy sync 后）

- Claude Code：`.claude/skills/<skill-name>/`
- Codex：`.agents/skills/<skill-name>/`
- 本 skill 内脚本/模板用相对路径（如 `scripts/…`、`执行清单.template.md`）
- 跨 skill 脚本用兄弟目录（如 `../uc-media-0070-package/scripts/…`）

## 兼容

旧 0010-position+0020-brief → 0010-product；旧 0030…0090 → 0020…0080。
