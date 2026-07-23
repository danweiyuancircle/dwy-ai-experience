# 第 1 章参考：apt / uv / pip 阿里云片段

通用片段，按基础镜像选用。**默认首选阿里云。**

---

## apt — Debian 12 (bookworm, deb822)

```dockerfile
RUN sed -i \
      's|deb.debian.org|mirrors.aliyun.com|g; s|security.debian.org|mirrors.aliyun.com|g' \
      /etc/apt/sources.list.d/debian.sources 2>/dev/null \
    || sed -i \
      's|deb.debian.org|mirrors.aliyun.com|g; s|security.debian.org|mirrors.aliyun.com|g' \
      /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends <packages> \
    && rm -rf /var/lib/apt/lists/*
```

## apt — Debian 11 (bullseye)

```dockerfile
RUN sed -i \
      's|http://deb.debian.org|https://mirrors.aliyun.com|g; \
       s|http://security.debian.org|https://mirrors.aliyun.com/debian-security|g' \
      /etc/apt/sources.list \
    && apt-get update
```

## apt — Ubuntu 22.04

```dockerfile
RUN sed -i \
      's|http://archive.ubuntu.com/ubuntu/|https://mirrors.aliyun.com/ubuntu/|g; \
       s|http://security.ubuntu.com/ubuntu/|https://mirrors.aliyun.com/ubuntu/|g' \
      /etc/apt/sources.list \
    && apt-get update
```

## apt — Ubuntu 24.04 (noble, deb822)

```dockerfile
RUN sed -i \
      's|http://archive.ubuntu.com/ubuntu/|https://mirrors.aliyun.com/ubuntu/|g; \
       s|http://security.ubuntu.com/ubuntu/|https://mirrors.aliyun.com/ubuntu/|g' \
      /etc/apt/sources.list.d/ubuntu.sources \
    && apt-get update
```

## apk — Alpine

```dockerfile
RUN sed -i 's|https://dl-cdn.alpinelinux.org|https://mirrors.aliyun.com|g' \
        /etc/apk/repositories \
    && apk update
```

---

## uv + pip 环境变量（推荐写在 Dockerfile 靠前）

```dockerfile
ENV UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple/ \
    UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
    PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
    PIP_TRUSTED_HOST=mirrors.aliyun.com
```

## 安装 uv（禁止默认 astral.sh）

```dockerfile
# ✅ 阿里云 PyPI
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ \
        --trusted-host mirrors.aliyun.com \
        "uv>=0.4"

# ❌ 国内易慢
# RUN curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 用 uv 装项目

```dockerfile
RUN uv pip install --system --no-cache .
# 或锁文件项目：
# RUN uv sync --frozen --no-dev
```

## 仅 pip（无 uv）

```dockerfile
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ \
        --trusted-host mirrors.aliyun.com \
        -r requirements.txt
```

## 项目级 uv（pyproject.toml，可选）

```toml
[[tool.uv.index]]
url = "https://mirrors.aliyun.com/pypi/simple/"
default = true
```

## 用户级 uv（~/.config/uv/uv.toml，可选；开发机详查 dwy-mirror-source）

```toml
[[index]]
url = "https://mirrors.aliyun.com/pypi/simple/"
default = true
```
