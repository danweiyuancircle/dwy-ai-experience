# 监控发布进程 + 通知结果

发布触发后监控进程直到终态，再输出结果文本。监控方式因 CI / 本地而异（项目步）。

## 监控

发布方式来自缓存 method：

- **CI（github-action / github-action-oidc）**：
  ```bash
  gh run watch "$(gh run list --workflow=<release.yml> --limit=1 --json databaseId --jq '.[0].databaseId')" --exit-status
  ```
  观察到失败时拉日志定位失败 job：`gh run view <run-id> --json jobs,conclusion`。
- **本地（local / testflight / maven / cocoapods / ohpm）**：用缓存的 `publish_cmd` 退出码判断，再做产物 / 渠道检查。

## verify

用缓存 `verify_cmd`，或按渠道验证新版本可见：

- npm：`npm view <pkg> version`
- PyPI：`pip index versions <pkg>`
- maven / ohpm / cocoapods：对应渠道版本查询
- TestFlight：App Store Connect 构建状态
- GitHub Release：`gh release view <tag>`
- 前端 / 后端：页面访问 / 版本接口 / 健康检查

verify 失败，发布不算完成。

## 通知结果（输出结果文本）

发布终态后在对话里输出结果摘要，不接外部通知：

- **成功**：平台 / 应用目录、版本号、产物、渠道、verify 结果
- **失败**：失败阶段、关键报错、下一步建议（重发 / bump / 修配置）

涉及删除远端 release / tag 的重发，必须先确认用户允许。
