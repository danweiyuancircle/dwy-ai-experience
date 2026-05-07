# Dockerfile 内换源代码片段

Linux 包管理（apt/apk/yum/dnf）和 Python pip 在 Dockerfile 内的换源代码片段。这些是**镜像构建时**的源，与本机用户配置无关，需要写到 Dockerfile 里。

## 通用原则

1. **基础镜像确定后再换源** — 不同 base image 用不同包管理（Ubuntu/Debian 用 apt，Alpine 用 apk，CentOS/RockyLinux 用 yum/dnf）
2. **多阶段构建只在需要安装包的阶段换** — 最终运行阶段如果不装包，不必加这些
3. **CI/CD 镜像构建可能不需要换源** — 部分 CI 已在境内或自建 mirror，按团队约定

---

## Debian / Ubuntu (apt)

### Ubuntu 22.04 / 24.04（Noble / Jammy）

Ubuntu 24.04 起 sources.list 改为 deb822 格式（`/etc/apt/sources.list.d/ubuntu.sources`），22.04 仍是老格式。

```dockerfile
# Ubuntu 22.04 (jammy)
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|https://mirrors.aliyun.com/ubuntu/|g; \
            s|http://security.ubuntu.com/ubuntu/|https://mirrors.aliyun.com/ubuntu/|g' \
        /etc/apt/sources.list \
    && apt-get update
```

```dockerfile
# Ubuntu 24.04 (noble)
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|https://mirrors.aliyun.com/ubuntu/|g; \
            s|http://security.ubuntu.com/ubuntu/|https://mirrors.aliyun.com/ubuntu/|g' \
        /etc/apt/sources.list.d/ubuntu.sources \
    && apt-get update
```

### Debian 11 / 12（Bullseye / Bookworm）

Debian 12 起也用了 deb822 格式（`/etc/apt/sources.list.d/debian.sources`）。

```dockerfile
# Debian 11 (bullseye)
RUN sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g; \
            s|http://security.debian.org|https://mirrors.aliyun.com/debian-security|g' \
        /etc/apt/sources.list \
    && apt-get update
```

```dockerfile
# Debian 12 (bookworm)
RUN sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' \
        /etc/apt/sources.list.d/debian.sources \
    && apt-get update
```

---

## Alpine (apk)

```dockerfile
RUN sed -i 's|https://dl-cdn.alpinelinux.org|https://mirrors.aliyun.com|g' \
        /etc/apk/repositories \
    && apk update
```

---

## CentOS / RockyLinux / AlmaLinux (yum / dnf)

### RockyLinux 9 / AlmaLinux 9

```dockerfile
RUN sed -e 's|^mirrorlist=|#mirrorlist=|g' \
        -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
        -i.bak /etc/yum.repos.d/rocky-*.repo \
    && dnf clean all
```

### CentOS 7（已 EOL，仍有遗留）

```dockerfile
RUN curl -o /etc/yum.repos.d/CentOS-Base.repo \
        https://mirrors.aliyun.com/repo/Centos-7.repo \
    && yum clean all && yum makecache
```

---

## Python pip 在 Dockerfile 内

不依赖容器内 `~/.config/pip/pip.conf`，直接在 RUN 命令中指定 `-i`：

```dockerfile
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ \
        --trusted-host mirrors.aliyun.com \
        -r requirements.txt
```

或写到环境变量供后续 RUN 沿用：

```dockerfile
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
ENV PIP_TRUSTED_HOST=mirrors.aliyun.com
RUN pip install --no-cache-dir -r requirements.txt
```

---

## uv 在 Dockerfile 内

```dockerfile
ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
RUN uv pip install --system -r requirements.txt
```

---

## Node 在 Dockerfile 内

```dockerfile
RUN npm config set registry https://registry.npmmirror.com \
    && npm install --production
```

或 pnpm：

```dockerfile
RUN pnpm config set registry https://registry.npmmirror.com \
    && pnpm install --frozen-lockfile
```

---

## Go 在 Dockerfile 内

```dockerfile
ENV GOPROXY=https://goproxy.cn,direct
RUN go mod download
```

---

## Rust / Cargo 在 Dockerfile 内

```dockerfile
RUN mkdir -p ~/.cargo \
    && echo '[source.crates-io]'                                  >  ~/.cargo/config.toml \
    && echo 'replace-with = "rsproxy-sparse"'                     >> ~/.cargo/config.toml \
    && echo ''                                                    >> ~/.cargo/config.toml \
    && echo '[source.rsproxy-sparse]'                             >> ~/.cargo/config.toml \
    && echo 'registry = "sparse+https://rsproxy.cn/index/"'       >> ~/.cargo/config.toml
```

---

## Maven 在 Dockerfile 内

```dockerfile
COPY <<'EOF' /root/.m2/settings.xml
<settings>
  <mirrors>
    <mirror>
      <id>aliyun</id>
      <mirrorOf>*</mirrorOf>
      <url>https://maven.aliyun.com/repository/public</url>
    </mirror>
  </mirrors>
</settings>
EOF
```

---

## 完整组合示例：Python 后端镜像

```dockerfile
FROM python:3.12-slim-bookworm

# 1. apt 换源
RUN sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' \
        /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. pip 换源
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
    PIP_TRUSTED_HOST=mirrors.aliyun.com

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

---

## 完整组合示例：Node 前端镜像

```dockerfile
FROM node:20.18.0-bookworm-slim AS builder

# 1. apt 换源（可选，build stage 用得多就加）
RUN sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' \
        /etc/apt/sources.list.d/debian.sources

# 2. pnpm 换源
RUN corepack enable && pnpm config set registry https://registry.npmmirror.com

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM nginx:1.26.2-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

---

## 注意事项

1. **不要在 Dockerfile 里写 `latest` 镜像 tag** — 见 `dwy-docker-image` skill
2. **`--trusted-host` 仅在 http 镜像源时需要** — https 镜像不需要这个参数，但加上无害
3. **多阶段构建复制配置** — 如果 builder 阶段配了源，runtime 阶段需要再配一次（不会自动继承）
4. **生产构建不要把 token / 私服密码写进 Dockerfile** — 用 BuildKit secrets 或 build-args
