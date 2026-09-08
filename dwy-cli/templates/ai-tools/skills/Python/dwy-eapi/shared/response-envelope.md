# 响应信封

所有接口返回：

```json
{
  "code": "SUCCESS",
  "message": "success",
  "data": {},
  "timestamp": 1775625000
}
```

- 成功：`code = "SUCCESS"`，`data` 是业务载荷（单体或 `PageData[T]`）
- 失败：`code` 是业务错误码（`NOT_FOUND` / `BUSINESS_ERROR` / `VALIDATION_ERROR`），HTTP 状态保持语义
- 校验错误 `VALIDATION_ERROR`：`data.errors: [{field, message}]`，field 含 `body.` / `query.` / `path.` 前缀

构造：`ApiResponse.ok(data)` 或 `ApiResponse.page(items, total, page, page_size)`，不直接实例化成功态。

错误响应不要业务代码拼信封 —— `raise NotFoundError("用户")`，handler 自动转。
