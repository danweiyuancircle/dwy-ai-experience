# AskUserQuestion 模板（按违规类型）

发现违规需要让用户决策时读这份。模板都用 `preview` 字段（用户能直接看到将要写入的那一行）。

## 通用措辞要点

- `question` 必须**指出当前问题**（"latest 不符合规范" / "redis:7 只有 major"），而不是泛泛"选个版本"
- `header` ≤12 字符，用 `<image> tag` / `多阶段` / `compose 分离` 这类
- 第一个 option 永远是推荐项，标 `(推荐)` / `(N-1 推荐)`
- `description` 必须含**理由**（为什么这个选项），含日期更好
- `preview` 用实际写入文件的那一行（`FROM xxx:tag` / `image: xxx:tag`）
- 选项 2-4 个；非生产关键服务不给 digest 选项

---

## 模板 1：tag 违规（最常用）

适用：`latest` / 浮动 tag（`stable` / `mainline` / `alpine` / `bookworm` 等单独使用）/ 单段版本号（`redis:7`）/ codename 不带版本号。

```jsonc
AskUserQuestion({
  questions: [{
    question: "nginx:latest 不符合规范（禁用 latest）。请选择固定版本：",
    header: "nginx tag",
    multiSelect: false,
    options: [
      {
        label: "1.26.2 (N-1 推荐)",
        description: "N-1 minor 系列最新 patch，发布 2024-08-28，已过早期回归窗口",
        preview: "image: nginx:1.26.2"
      },
      {
        label: "1.27.3 (最新稳定)",
        description: "最新稳定版，2024-11-26 发布，新功能尝鲜场景再选",
        preview: "image: nginx:1.27.3"
      },
      {
        label: "1.26.2 + digest (生产关键)",
        description: "钉到 digest，image 100% 不可篡改，生产网关推荐",
        preview: "image: nginx:1.26.2@sha256:..."
      }
    ]
  }]
})
```

---

## 模板 2：Dockerfile 结构违规

适用：单阶段构建 / 缺 USER / 缺 .dockerignore / 包含 dev 依赖。

```jsonc
AskUserQuestion({
  questions: [{
    question: "Dockerfile.prod 是单阶段构建，镜像会包含 dev 依赖（违反多阶段约束）。如何处理？",
    header: "多阶段",
    multiSelect: false,
    options: [
      {
        label: "改为 builder + runtime 多阶段",
        description: "我把当前 Dockerfile 重写成 builder + 精简 runtime，仅复制必要文件",
        preview: "FROM python:3.11-slim AS builder\n...\nFROM python:3.11-slim\nCOPY --from=builder ..."
      },
      {
        label: "保留单阶段（说明原因）",
        description: "比如你正在写 Dockerfile.dev，或镜像本身就是 dev/调试用",
        preview: "(保留现状)"
      }
    ]
  }]
})
```

---

## 模板 3：compose 结构违规

适用：未分离 dev/prod / prod 暴露内部端口 / 缺 healthcheck / 硬编码密码。

```jsonc
AskUserQuestion({
  questions: [{
    question: "项目只有一份 docker-compose.yml，dev 和 prod 配置混合（违反 dev/prod 分离）。如何处理？",
    header: "compose 分离",
    multiSelect: false,
    options: [
      {
        label: "拆分为 dev.yml + prod.yml",
        description: "我把当前 compose 拆成两份：dev 暴露端口 + 应用宿主机跑，prod 不暴露端口 + 全容器化 + healthcheck",
        preview: "docker-compose.dev.yml\ndocker-compose.prod.yml"
      },
      {
        label: "暂不拆分（仅本地原型）",
        description: "如果只是临时原型不上线，可以先不拆，但记得上线前必须分离",
        preview: "(保留现状)"
      }
    ]
  }]
})
```

---

## 模板 4：批量 tag 违规（一次询问多镜像）

一份 compose 文件含 postgres + redis + nginx 都用了 latest 时，并列询问。

```jsonc
AskUserQuestion({
  questions: [
    {
      question: "postgres:latest → 选固定版本：",
      header: "postgres tag",
      multiSelect: false,
      options: [/* 同模板 1 结构 */]
    },
    {
      question: "redis:latest → 选固定版本：",
      header: "redis tag",
      multiSelect: false,
      options: [/* 同模板 1 结构 */]
    },
    {
      question: "nginx:latest → 选固定版本：",
      header: "nginx tag",
      multiSelect: false,
      options: [/* 同模板 1 结构 */]
    }
  ]
})
```

**约束**：一次最多 4 个并列 question；超过分批询问。

---

## 用户选了 "Other" 自定义版本时

按用户输入的值写入，但口头提醒一句："你选的 `xxx:Y.Y.Y` 不在 N-1 推荐范围内（当前推荐 N-1 是 `xxx:Z.Z.Z`），确认是出于具体原因吗？"

不要拒绝写入，但要让用户知道这是非常规选择。
