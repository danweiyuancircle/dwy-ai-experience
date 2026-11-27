# Changelog

## 0.1.0

- 新增 `DwySignInAdapter` 抽象与统一凭据模型 `DwySocialIdentity`、固定
  错误码 `DwySignInException`。
- 内置 Apple（sign_in_with_apple 8.2.0）与 Google（google_sign_in 7.2.0）
  两个 adapter；凭据透传，验证由业务后端完成。
