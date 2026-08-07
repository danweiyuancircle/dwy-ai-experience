---
name: uc-media-knowledge-town
description: |
  将科普脚本制作成“知识小城”纸片电影：固定 LLM-S01-ChatDoor 的贴纸视觉系统，允许不同主题自由设计场景、道具和镜头，并生成可由 Remotion 渲染的素材、镜头与对轨数据。用于 0050 锁定视觉、0060 生成和验收角色/道具/档案贴纸、0070 组装 cue-timeline 或 0080 Remotion 制作；适用于二维纸片拼贴、边讲边展示、字幕/口播/BGM/音效同步的知识视频。
---

# 知识小城纸片电影制作标准

使用本 skill 时，保留现有流水线分工：0040 决定说什么，0050 选风格，0060 管素材，0070 生成机读对轨包，0080 生成 Remotion 工程。不要另建平行视频流程。

本 skill 分成两层：**频道贴纸系统固定**，以 LLM `S01PaperFilmPreview` 的纸张、描边、阴影、强调色、名牌、档案框和底部对白框为母版；**主题叙事世界可变**，每期可自由选择空间、道具、构图与镜头。不要把 LLM 的聊天门、手机或 AI 主题当作跨集必需元素。

## 风格锁定

在 `0050-design/design-lock.md` 写入：

```yaml
style_id: knowledge-town-paper-film-v1
production_stack: remotion
sync_source: media/0070-package/cue-timeline.json
```

读取 [`references/style-guide.md`](./references/style-guide.md)、[`references/sticker-asset-production.md`](./references/sticker-asset-production.md)、[`references/cinematic-direction.md`](./references/cinematic-direction.md) 和频道角色真源 `docs/知识小城频道角色规范.md`，再把 [`assets/knowledge-town-paper-film-v1.json`](./assets/knowledge-town-paper-film-v1.json) 复制到本集 `0060-assets/` 作为可改预设。品牌图标必须先从 `shared/icons/brands/` 取正式文件。

0060 先按贴纸规范生成或采购素材，再在深海军蓝与暖米纸底色检查透明边缘。通过后才可登记 `shared/` 并复制进本集；真实截图保持原貌，必须放入统一档案贴纸框。不得为某一主题另起描边、阴影、卡片、箭头或字幕体系。

## 对轨工作流

1. 用 0040 的定稿口播产生配音和逐句字幕；配音真实时长是唯一时长基准。
2. 为每句字幕指定一个 `cueId`、一个 `visualAction` 和零到多个 SFX。
3. 运行 `scripts/build_cue_timeline.py` 合并字幕、视觉 beats 与预设，生成 `0070-package/cue-timeline.json`。
4. 运行 `scripts/validate_cue_timeline.py`；失败时回到 0040/0060 修正，禁止在 0080 私自改时码。
5. 在 Remotion 使用 `assets/remotion/` 的组件模板：一个 timeline 同时驱动旁白、字幕、动作和音效。

```bash
python3 scripts/build_cue_timeline.py \
  --captions media/0040-script/captions-remotion-strict.json \
  --beats media/0070-package/caption-visual-beats.json \
  --preset media/0060-assets/knowledge-town-paper-film-v1.json \
  --voice audio/voice/s01-cn-v1.wav \
  --output media/0070-package/cue-timeline.json
python3 scripts/validate_cue_timeline.py media/0070-package/cue-timeline.json
```

## 硬规则

- 一个 `cueId` 只讲一个新信息；视觉动作在字幕开始后 2–4 帧预备，关键词在本 cue 的 40%–55% 出现。
- 先为每个 cue 写 `事实来源 → 主问题 → 主动作 → 可见结果 → 术语揭示`；画面中出现的文字、年份、因果和示例必须可回溯至 0030 facts 或已批准口播。类比必须标明是类比，不能把道具名称当成技术事实。
- 一个 cue 最多 `1 主角 + 1 道具 + 1 信息对象`，最多一条从原因到结果的运动路径。下一 cue 改讲新事时，先将旧元素收拢、淡出或转成转场物，禁止叠加成信息板。
- **cue 场景图（硬门槛）**：实现前必须为每个 cue 列出 `elementId / 角色 / 文字来源 / 入场 / 落点 / 退场 / z-index 层`。当前 cue 只能保留本 cue 的对象，或最多一个已声明的转场物；上一 cue 的普通对象必须在新 cue 主动作开始前退场，禁止隐式继承造成叠字或残留道具。
- **层级与依赖（硬门槛）**：层级固定为 `背景 0–9 → 舞台 10–19 → 连线/光束 20–29 → 道具 30–39 → 可读文字卡 40–49 → 前景贴纸 50–59 → 字幕 60+`。连线必须低于它指向的卡片，且只能在两个对象的空隙中存在；箭头线、箭头尖、发光和说明标签必须继承同一可见性与退场状态，禁止出现孤立线条、孤立箭头或标签滞留。
- **文字白名单（硬门槛）**：屏幕上的每一段文字必须是“当前口播术语、事实例子、当前 cue 关键词或必要的操作标签”之一；不在 cue 场景图中的文字、数字、装饰性标签和重复术语一律不得出现。顶部关键词已表达的术语，内容区不得再重复。
- **视觉语义（硬门槛）**：每个圆圈、箭头、光晕、线条和图标都必须在场景图中写明“指向谁 / 表示什么 / 何时消失”。没有叙事对象的装饰图形不得出现；高亮必须贴合被强调对象的轮廓，不能用泛化圆圈圈住一片空白。箭头必须从可见的原因对象出发、停在结果对象外沿，路径本身要能读出方向与因果。
- **箭头原语（硬门槛）**：同一集只允许一套关系箭头原语：深蓝描边 + 珊瑚红纸带 + 固定比例的小箭头头部 + 绘制入场。关系默认使用对象之间的水平直连；不得用弧线、绕行线或流程图式折线增加装饰。不得混用 CSS 三角形、默认字符箭头、无描边线或不同颜色的箭头。空间不足时先重排对象，禁止把箭头压缩成只剩箭头头部。
- 术语只在观众看懂动作后的结果帧出现一次；顶部关键词、中心贴纸和字幕不可重复同一术语。术语贴纸出现时，顶部关键词必须让位。
- 每镜采用 `base_bg → content → text_sticker` 三层；不得用一张完成态大图替代渐进揭示。
- **文字与路径防碰撞（硬门槛）**：每张可读文字卡、术语贴纸、角色名牌的可见边界（含描边与阴影）之间至少留 `24px`；连线、箭头、光束只能停在对象外沿，不得压过文字、描边、阴影或进入文字卡的点击/阅读区。需要指向时，箭头尖端与对象外沿保留 `8–16px` 间隙。
- 禁止用不完整边框、孤立的半截箭头、无闭合折角来模拟纸片尾巴或连接关系；纸条拐角必须是完整闭合形状，连接线须在两个对象的空隙中可见且语义单一。
- 底部 180px 是字幕带；关键内容的包围盒不得进入。
- BGM、SFX、旁白分别建资产；旁白存在时 BGM 自动压低。只使用原创或许可明确可商用的音频和声音。
- `cue-timeline.json` 是 0070 对轨真源；Remotion 组件不得自行写死字幕或 SFX 帧。
- `LLM-S01-ChatDoor` 是频道贴纸系统的唯一质量母版，不是主题故事模板：先有角色要解决的事，再进入可感知的空间，由本主题英雄道具完成一次可见的变化，最后落在一个结果画面。
- 每个正式场景必须提交独立 Remotion composition；先做 8–20 秒动态样片并获确认，再推广到全场。不得只交付整片预览。
- 卡片、时间线节点、流程箭头只能作为道具的短暂状态，不能并排常驻承担讲解；禁止“背景 + 三张大卡 + 箭头 + 字幕”的成片结构。
- 每场至少包含：前/中/后景，角色或道具的因果动作，一次镜头推进/拉远/穿行/转场，以及动作落点音效。没有这些只可标为预演，不可标为正式镜头。
- 每个 cue 必须同时具备：`1 个叙事动作 + 1 个低频质感微动 + 1 个明确落点`。叙事动作推动因果（递交、选择、拆开、扫查、折叠等）；质感微动只增强纸片空间（纸张轻呼吸、光圈扩散、景深视差、阴影微偏移等），不得替代叙事；落点必须在动作结束时清晰可见，并配对应 SFX 或静默停顿。
- 禁止无意义的漂浮、循环旋转、待机晃动和与画面无关的音效；角色只在入场、指向、递交、反应或收束等叙事动作时动画。
- 每场先输出 3–4 张关键帧（建立、推进、术语结果、转场），逐张检查：无遮挡、无重复术语、无并排卡片墙、无事实越界；并以文字卡的描边/阴影外扩边界复核最小间距、连线终点与箭头尖端。通过后才渲染独立预览。
- **动态碰撞验收（硬门槛）**：除建立/结果帧外，还必须抽检每段运动的 `25% / 50% / 75% / 90%` 帧。检查真实包围盒（文字、描边、阴影、缩放后的范围）是否相撞；尤其检查对象汇聚时不可落到同一坐标。任何重叠、遮字、无关残留或未绑定的线条，必须先修复场景图和生命周期，不能只靠微调坐标遮掩。

## 资源

- 风格规则：[`references/style-guide.md`](./references/style-guide.md)
- 素材生成与透明验收：[`references/sticker-asset-production.md`](./references/sticker-asset-production.md)
- 电影化导演规则与镜头配方：[`references/cinematic-direction.md`](./references/cinematic-direction.md)
- 可复制预设：[`assets/knowledge-town-paper-film-v1.json`](./assets/knowledge-town-paper-film-v1.json)
- 对轨构建与校验：[`scripts/`](./scripts/)
- Remotion 组件模板：[`assets/remotion/`](./assets/remotion/)
