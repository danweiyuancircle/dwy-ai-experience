# 测试范围

2026-11-16：Flutter3.50.0 / Dart3.14.0，8项测试通过；使用真实解码、本机 HTTP 与临时文件，不代表原生设备验收通过。

| 测试文件 / 用例 | 目标 |
| --- | --- |
| source_test.dart / network cache keys isolate accounts | 同一 URL/认证头在不同账户命名空间不共用内存 Provider 键，诊断 source 文本不包含 URL/Token |
| source_test.dart / rejects unsafe URLs and invalid dimensions | 非 HTTP(S)、相对地址、userinfo、fragment、空资源/缓冲区和非法尺寸在外部边界被拒绝 |
| source_test.dart / asset, local and memory sources | 四类入口复用 Flutter/缓存图片 Provider；解码边界保持原始比例 |
| source_test.dart / namespace ownership | 同名缓存不能重复持有，创建后立即关闭会等待仓库初始化，关闭后拒绝旧实例并允许新实例接管 |
| source_test.dart / clear waits for an active response | 真实本机 HTTP 响应尚未完成时，清理等待其落盘再删除，不虚报清理完成 |
| image_test.dart / memory images decode to bounds | 实际解码后像素边界和比例正确，Widget 固定逻辑尺寸并提供语义标签 |
| image_test.dart / failed image keeps layout | 无效图片可见失败与重试，大字体窄布局不溢出、不抛未处理异常 |
| image_test.dart / network prefetch caches | 本机 HTTP 503 返回失败；恢复后可重试；二次命中不重复请求；指定失效重新请求；清理 A 不影响 B |

主代理集成后补充：浅深色 Playground、手机图片列表滚动、内存/帧时间、Android/iOS 原生磁盘缓存、Web 明确的缓存限制。测试夹具仅使用生成的纯色 PNG 与回环 HTTP，不上传用户图片。
