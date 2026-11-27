/// 提供商无关的第三方登录：业务面对统一的 adapter 接口与凭据模型，
/// 平台登录实现（Apple / Google，未来可加微信等）各自独立注入。
///
/// 凭据只透传不验证：identityToken 必须由业务后端向平台验证后换发
/// 自家会话；本库不连后端、不落盘、不打日志。
library;

export 'src/adapters.dart';
export 'src/apple.dart';
export 'src/google.dart';
export 'src/models.dart';
