# 私有源码与产物分发

权威源码位于私有仓库 `https://github.com/danweiyuancircle/dwy-ai-experience`。新版本不再发布到公共 npm/PyPI；旧公开版本保留供既有项目使用。

## 发布路径

GitHub Actions 工作流 `.github/workflows/private-release.yml` 在私有仓库运行 Web/Python/Swift 回归和构建。只有标准 SwiftPM 语义化标签（首版 `0.4.0`）才能创建私有 GitHub Release；分支构建不创建发布。

发布包括五个 npm tgz（EUI、EKIT、admin-kit、auth-web、CLI）、EAPI/auth Python wheel 与 sdist、`release-manifest.json` 和 `SHA256SUMS`。SwiftPM 使用同一源提交的 Git 标签。工作流只使用临时 `GITHUB_TOKEN`，不配置长期 npm/PyPI 发布凭据；公开仓库可见性检查失败时立即拒绝。

npm 包启用 `private: true`；两个 Python 包使用 `Private :: Do Not Upload` classifier，PyPI 会原生拒绝带该标记的上传，见 [PyPI 官方说明](https://pypi.org/classifiers/)。这些保护不影响私有归档构建和本地安装。

本地 Web 验证使用 `.node-version` 指定的 Node 22.14.0，与 CI 一致。本机若使用 Node 26，其原生 Web Storage 会干扰旧版 Vitest/jsdom 的全局存储注入；可局部设置 `NODE_OPTIONS=--no-experimental-webstorage` 运行测试，无需更改业务存储实现。

## 下载与安装

使用有权读取仓库的 `gh` 账号或 CI 短期身份认证。跨业务仓库 CI 应配置有只读目标仓库权限的 GitHub App 短期令牌或受控只读访问，不能把私有凭据写进依赖 URL、包配置或提交文件。

```sh
# 在共享仓库根目录执行。
python3 scripts/private_release.py download --tag 0.4.0 --directory /tmp/dwy-private-0.4.0
```

下载命令要求目标目录为空，并验证每份产物实际大小和 SHA256。`release-manifest.json` 记录源提交，不能把后续同版本本地重建包当作已发布包。

Python 消费者显式安装已下载的 EAPI/auth wheel，避免公共索引解析成旧包；其他第三方依赖按消费项目锁文件安装。开发时可使用固定提交的私有 Git 依赖并指定子目录。

Node 消费者从下载目录安装所需 tgz，EUI/EKIT/admin-kit 等内部依赖也应显式选用同一私有发布产物。不能把认证 cookie 或 Google/管理员凭据放进 npm 配置或浏览器持久存储。

Apple 消费者在 Xcode/SwiftPM 配置私有 Git 访问，依赖 URL 为 `https://github.com/danweiyuancircle/dwy-ai-experience.git`，版本 `0.4.0`。产品名保持 CoreKit、CacheKit、PurchaseCore、AuthCore 等，SPM 仓库 identity 改为 `dwy-ai-experience`。

## 边界

仓库私有化不会撤回已被下载的历史公开代码或包。当前方案不要求开通收费私有 registry，也不引入新常驻分发服务；后续可把同一产物推入私有 npm/Python registry。

真实 Google OAuth、Apple 购买以及产品后端部署需要独立配置和验收；私有发布测试只证明构建、发布、读取和安装链，不冒充真实登录验收。
