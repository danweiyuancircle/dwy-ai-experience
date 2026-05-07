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

## Docker 加速器（重点）

Docker 镜像加速分**两类**，互不替代：

### 类型 1：docker.io 加速（registry-mirrors）

仅作用于 Docker Hub（`docker.io`）。配置在 `~/.docker/daemon.json`：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
```

可选加速器：

| 加速器 | URL | 备注 |
|--------|-----|------|
| DaoCloud | `https://docker.m.daocloud.io` | **首选**，免登录、稳定 |
| 中科大 | `https://docker.mirrors.ustc.edu.cn` | 高校镜像 |
| 网易 | `https://hub-mirror.c.163.com` | 偶尔波动 |
| 阿里云专属 | `https://<your-id>.mirror.aliyuncs.com` | 阿里云用户专属，需登录获取 |
| 腾讯云 | `https://mirror.ccs.tencentyun.com` | 仅腾讯云内网 |

### 类型 2：非 docker.io registry 加速

**`registry-mirrors` 字段对 gcr/ghcr/quay/k8s/mcr/nvcr 等其他 registry 完全无效**。要加速这类 image，必须**改 image 引用本身**。

DaoCloud 维护的 11 个 registry 镜像（实测全部可达）：

| 源 registry | 镜像域名 | 用途 |
|-------------|---------|------|
| `docker.io` | `docker.m.daocloud.io` | Docker Hub（也可走 registry-mirrors） |
| `gcr.io` | `gcr.m.daocloud.io` | Google Container Registry |
| `ghcr.io` | `ghcr.m.daocloud.io` | GitHub Container Registry |
| `quay.io` | `quay.m.daocloud.io` | Red Hat Quay |
| `k8s.gcr.io` | `k8s-gcr.m.daocloud.io` | Kubernetes 旧仓库（已迁出） |
| `registry.k8s.io` | `k8s.m.daocloud.io` | Kubernetes 当前官方 registry |
| `mcr.microsoft.com` | `mcr.m.daocloud.io` | Microsoft Container Registry |
| `nvcr.io` | `nvcr.m.daocloud.io` | NVIDIA Container Registry |
| `docker.elastic.co` | `elastic.m.daocloud.io` | Elastic 官方镜像 |
| `dhi.io` | `dhi.m.daocloud.io` | Docker Hub Images |
| `registry.ollama.ai` | `ollama.m.daocloud.io` | Ollama 模型（beta） |

**用法示例：**

```bash
# 原本（拉不动）
docker pull gcr.io/google-containers/pause:3.9
docker pull ghcr.io/astral-sh/uv:latest
docker pull registry.k8s.io/kube-apiserver:v1.30.0

# 走加速（改前缀域名）
docker pull gcr.m.daocloud.io/google-containers/pause:3.9
docker pull ghcr.m.daocloud.io/astral-sh/uv:0.5.0
docker pull k8s.m.daocloud.io/kube-apiserver:v1.30.0
```

```dockerfile
# Dockerfile 内同样改前缀
FROM ghcr.m.daocloud.io/astral-sh/uv:0.5.0 AS uv
FROM gcr.m.daocloud.io/distroless/python3:nonroot
```

**关键限制：**
- 这套加速**不能配在 daemon.json 里实现透明代理**（registry-mirrors 字段只识别 docker.io）
- 必须显式写入 image 引用，无法自动改写
- containerd / Kubernetes 可以用 `mirrors` 配置全局映射，但 Docker 不行

## 私服识别规则

`check_mirrors.py` 检测到以下模式时识别为企业私服，**不修改**：

- 域名包含 `nexus`、`artifactory`、`harbor`、`internal`、`corp`、`company`、`pypi.local`、`registry.local`
- IP 地址形式（不论公网还是内网）
- 端口 `8081`、`8082`、`5000`（Nexus / Harbor 常见端口）
- 路径包含 `/repository/`（Nexus 标志路径）
