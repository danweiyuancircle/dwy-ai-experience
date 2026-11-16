# dwy_network 测试范围

2026-11-16：Flutter3.50.0 内置 Dart3.14.0，14项 Dart 测试通过；不代表移动端原生验收完成。

| 用例 | 验证目标 |
| --- | --- |
| decodes product-specific JSON without a fixed envelope | 无固定 envelope 的解码与 HTTP 元数据 |
| distinguishes protocol failure, HTTP failure and cancellation | 无效 JSON、HTTP 503、请求取消的分类 |
| rejects other origins and does not follow redirects with credentials | 跨 origin 请求与重定向拒绝 |
| does not replay failed writes and reports receive timeout | POST 不自动重放，真实接收超时 |
| download reports real bytes into its own directory | 下载完整内容、真实字节进度及返回目录所有权 |
| concurrent downloads never overwrite files in their shared parent | 并发下载目录独立，不覆盖中途创建的父目录用户文件 |
| failed and cancelled downloads do not leave a final file | HTTP失败及取消不提交最终文件 |
| preserves product failure payload and cause without unsafe error text | 显式读取业务错误数据，保留cause/stack且默认文本脱敏 |
| upload sends multipart file and real progress | multipart 文件内容及实际发送进度 |
| network diagnostics omit request credentials, queries and bodies | 网络诊断不记录凭据和正文 |
| close cancels and awaits active requests, rejects later work | 关闭等待活动请求，拒绝新工作 |
| response diagnostics cannot turn an accepted POST into failure | 响应阶段日志关闭仍返回 POST 成功，诊断错误单独可观察 |
| HTTP and cancellation failures survive an unavailable diagnostic sink | 日志不可用不覆盖 HTTP 与取消分类 |
| transform timeout remains a timeout classification | Dio transformTimeout 映射稳定超时分类 |

未覆盖：HTTPS 证书错误、真实文件清理失败、实际移动网络切换、系统挂起及平台文件授权；高级 transport 直接调用不属于 DWY API 的追踪范围。
