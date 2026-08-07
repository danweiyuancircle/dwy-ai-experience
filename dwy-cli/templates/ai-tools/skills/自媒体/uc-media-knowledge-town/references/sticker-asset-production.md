# 知识小城贴纸素材生产

在 0060 生成或采购素材前，先读取 `knowledge-town-paper-film-v1.json` 的 `visualTokens` 与 `assetAcceptance`。

## 通用提示词前缀

```text
2D paper-cut collage sticker, warm rice-paper texture, deep navy #14213d thick ink outline, crisp offset deep-navy paper shadow, warm cream paper base, small accents only in bright yellow #ffd161, teal #77dfd1 and coral pink #ff9cb9, tactile layered paper, clean readable silhouette, no text, no logo, no UI, no watermark, no photorealism, no 3D render
```

### 变量模板

| 素材 | 在前缀后补充 |
|---|---|
| 角色 | `full-body [role and action], transparent-background source, generous padding, no cast shadow` |
| 单道具 | `one oversized [topic prop] showing [single action], transparent-background source, generous padding` |
| 空景 | `[topic space] with foreground, midground and background layers, empty lower 180px subtitle area, no character, no text` |
| 档案框 | `empty paper archive frame with wide image window, no text, transparent-background source` |

## 透明资产验收

1. 生图阶段使用单一、远离主体配色的纯色键背景；不得有渐变、地面、投影或反射。
2. 转换为 alpha PNG 后，在 `#14213d` 和 `#f4e8c6` 两种底色预览。
3. 检查完整轮廓、头发和深色线稿；不能有洋红/绿色残边、黑洞、锯齿或被擦除的细节。
4. 通过后，将正式 PNG、来源、版本、角色/道具用途与深浅底检查结果登记进共享资产表；色键源图只留作溯源。
5. 未通过验收的文件不得复制到新集或标记为 `cross_episode`。

## 不可变与可变

不可变：纸张、深海军蓝描边与硬阴影、强调色、贴纸卡、档案框、箭头和对白框。可变：主题空间、主题道具、角色动作、镜头语言和故事节奏。
