# Apple 四层速查

完整规则：[apple/Docs/ARCHITECTURE.md](ARCHITECTURE.md)。

| 层 | 单端与双端统一职责 | 新项目落点 |
| --- | --- | --- |
| ① App 装配层 | 入口、DI、路由、scene/window 生命周期 | `ios/App`、`macos/App` |
| ② Features 功能层 | 页面、页面状态、业务定制 UI | 本端 `Features`、`BusinessUI`；按需产品共享 UI 包 |
| ③ BizFoundation 业务基础层 | 共享业务规则与协议、本端业务适配 | `packages/<Product>Core`；按需本端 `Platform` |
| ④ Foundation 通用基础层 | 跨产品基础能力、通用 UI 与系统适配 | 实际 AppleAppKit products，不建空层锚点 |

```text
① → ② → ③ → ④
①② → ④ UI 产品
① → 本端③ Platform → 共享③协议
```

目录和包不是层级：BusinessUI 属于②，产品平台适配属于③，均不新增第五层。共享核心不依赖 UI、应用壳或具体平台实现；平台框架访问由对应适配负责，生命周期由 App 装配。

满足需求的共享 UI 直接使用，禁止同功能再包装；业务定制收敛在 BusinessUI，缺口可自行实现，不强制先补库。真正双端共用业务 UI 才提成包。

新项目按 ios、macos、apple 三种形态生成，未选平台不生成。依赖在直接消费者声明，多处约束保持一致。产品内包用相对 path，外部基础库用已发布精确版本。
