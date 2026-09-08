# 分层

- **service 层**抛业务异常（`NotFoundError("用户")` / `BusinessError("余额不足", code="INSUFFICIENT_BALANCE")`），不感知 HTTP。
- **router 层**不写 try/except，由 `register_exception_handlers(app)` 统一转成 `ApiResponse` 信封。
- **禁止**在 service 层抛 `HTTPException` —— 会绕过统一 handler。
