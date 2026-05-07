# 镜像源 URL 对照表

各加速服务的 URL 由 `check_mirrors.py` / `apply_mirrors.py` 中的 `MIRRORS` 字典维护。本文件作为**人类可读的索引**，便于审阅、迁移、扩展新工具。

如需更新 URL，请同时改脚本里的 `MIRRORS` 字典和本文档，保持一致。

## 默认推荐：阿里云

阿里云覆盖最全、BGP 多线、对外网无依赖、稳定性高，故作默认。

| 工具 | URL | 说明 |
|------|-----|------|
| pip | `https://mirrors.aliyun.com/pypi/simple/` | PyPI 镜像 |
| uv | `https://mirrors.aliyun.com/pypi/simple/` | 与 pip 共用 |
| poetry | `https://mirrors.aliyun.com/pypi/simple/` | 同上 |
| npm | `https://registry.npmmirror.com` | npmmirror（原 npm.taobao 已迁移） |
| pnpm | `https://registry.npmmirror.com` | 共用 |
| yarn | `https://registry.npmmirror.com` | 共用 |
| Docker | `https://docker.m.daocloud.io` | DaoCloud 加速器，免登录 |
| Go (GOPROXY) | `https://goproxy.cn,direct` | 七牛云维护 |
| Cargo | `sparse+https://rsproxy.cn/index/` | 字节跳动维护 |
| Maven | `https://maven.aliyun.com/repository/public` | 综合公共仓库 |
| Gradle plugin | `https://maven.aliyun.com/repository/gradle-plugin` | gradle 插件库 |
| Homebrew brew.git | `https://mirrors.aliyun.com/homebrew/brew.git` | brew 仓库 |
| Homebrew core | `https://mirrors.aliyun.com/homebrew/homebrew-core.git` | core formulae |
| Homebrew bottles | `https://mirrors.aliyun.com/homebrew/homebrew-bottles` | 二进制包 |
| Flutter PUB | `https://pub.flutter-io.cn` | flutter pub |
| Flutter STORAGE | `https://storage.flutter-io.cn` | flutter SDK |

## 备选：清华 TUNA

教育网友好，混合源最完整。Homebrew 上清华源比阿里维护更新更勤。

| 工具 | URL |
|------|-----|
| pip | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| npm | `https://registry.npmmirror.com`（清华无 npm 镜像，回退 npmmirror） |
| Docker | `https://docker.m.daocloud.io`（清华无 docker 镜像，回退 daocloud） |
| Go | `https://goproxy.cn,direct`（清华无 GOPROXY，回退 goproxy.cn） |
| Cargo | `sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/` |
| Maven | `https://maven.aliyun.com/repository/public`（清华无 maven，回退 aliyun） |
| Homebrew brew.git | `https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git` |
| Homebrew core | `https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git` |
| Homebrew bottles | `https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles` |
| Flutter PUB | `https://pub.flutter-io.cn`（沿用） |

## 备选：中科大 USTC

| 工具 | URL |
|------|-----|
| pip | `https://mirrors.ustc.edu.cn/pypi/simple/` |
| npm | `https://registry.npmmirror.com` |
| Docker | `https://docker.m.daocloud.io` |
| Go | `https://goproxy.cn,direct` |
| Cargo | `sparse+https://mirrors.ustc.edu.cn/crates.io-index/` |
| Maven | `https://maven.aliyun.com/repository/public` |
| Homebrew brew.git | `https://mirrors.ustc.edu.cn/brew.git` |
| Homebrew core | `https://mirrors.ustc.edu.cn/homebrew-core.git` |
| Homebrew bottles | `https://mirrors.ustc.edu.cn/homebrew-bottles` |
| Flutter PUB | `https://pub.flutter-io.cn` |

## 已弃用（必须迁移）

| 旧 URL | 状态 | 替代 |
|--------|------|------|
| `https://registry.npm.taobao.org` | 2022-05 已停止维护，证书过期 | `https://registry.npmmirror.com` |
| `https://registry.npmjs.cf` | 已停止 | `https://registry.npmmirror.com` |
| `https://mirrors.aliyun.com/pypi/`（无 `simple/`）| 路径错误 | `https://mirrors.aliyun.com/pypi/simple/` |
| `http://...` 任何镜像源 | 不安全 | 一律 `https://` |

## Docker 加速器对比

Docker Hub 加速器经常有变动，建议保留多个备选：

| 加速器 | URL | 备注 |
|--------|-----|------|
| DaoCloud | `https://docker.m.daocloud.io` | **首选**，免登录、稳定 |
| 中科大 | `https://docker.mirrors.ustc.edu.cn` | 高校镜像 |
| 网易 | `https://hub-mirror.c.163.com` | 偶尔波动 |
| 阿里云专属 | `https://<your-id>.mirror.aliyuncs.com` | 阿里云用户专属，需登录获取 |
| 腾讯云 | `https://mirror.ccs.tencentyun.com` | 仅腾讯云内网 |

`apply_mirrors.py` 默认写入 `["docker.m.daocloud.io", "docker.mirrors.ustc.edu.cn"]` 双源，提高可用性。

## 私服识别规则

`check_mirrors.py` 检测到以下模式时识别为企业私服，**不修改**：

- 域名包含 `nexus`、`artifactory`、`harbor`、`internal`、`corp`、`company`、`pypi.local`、`registry.local`
- IP 地址形式（不论公网还是内网）
- 端口 `8081`、`8082`、`5000`（Nexus / Harbor 常见端口）
- 路径包含 `/repository/`（Nexus 标志路径）
