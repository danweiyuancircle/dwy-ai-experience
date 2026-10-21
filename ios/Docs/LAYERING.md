# 四层目录速查

全文：[ARCHITECTURE.md](./ARCHITECTURE.md)

```
App/  Features/  BizFoundation/  Foundation/
 ①       ②            ③              ④
```

| 层 | 目录 | Product |
|----|------|---------|
| ① | App/ | App target |
| ② | Features/ | 编入 App target |
| ③ | BizFoundation/ | `BizFoundation` |
| ④ | Foundation/ + 骨架 path | CoreKit LogKit L10nKit CacheKit DesignCore DesignKit* PurchaseCore |

依赖：`①② → ③ → ④`；`①② → ④`。
