# uc-media-comic-kit · 快速自测

## 例 1：热词镜

输入：「A02 热词砸入，漫画风」

期望输出包含：

- base_bg 单独一行  
- 至少 5 个 content/sticker enter_order  
- 一句 text_sticker 问句  
- 明确禁止 full_composite  

## 例 2：产品 Logo

输入：「四个产品出场」

期望：

- logo 行 method 为 copy_lib 或 logo_on_plate  
- 禁止 ai 生成 ChatGPT 假标  
- 框可漫画化  

## 例 3：简洁渐进 + 事实

输入：「A01 四个产品 + 写上 GPT-5 和假绿标」

期望：

- 拒绝假标；Logo 用 copy_lib  
- 产品名仅事实列表中的正式名  
- 关键词贴纸渐进，不一次贴满长说明  

## 反例

| 输入 | 正确反应 |
|------|----------|
| 一张含全部热词+机器人的完成图 | 拒绝 → 分层 + enter_order |
| 屏上大段定义当主文案 | 拒绝 → 改短贴纸 + 口播承载定义 |
| AI 画「像 ChatGPT 的图标」 | 拒绝 → 真实 logo 文件 |
| 生图 prompt 要求图上排满说明 | 改写 prompt：单主体、留白、少字 |
