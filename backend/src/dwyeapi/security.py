"""JWT 令牌与 bcrypt 密码哈希工具。

封装 python-jose 与 bcrypt,业务代码统一通过本模块做认证凭证处理。
所有函数保持无状态 — 密钥和算法由调用方以参数显式传入,方便在不同环境或密钥版本之间切换。
"""

from datetime import timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from dwyeapi import dt


def hash_password(password: str) -> str:
    """生成密码的 bcrypt 哈希。

    每次调用都会生成新的随机盐,相同明文多次调用结果不同,符合 bcrypt 推荐用法。

    Args:
        password: 用户侧传入的原始密码明文。

    Returns:
        可直接入库的 bcrypt 哈希字符串(含盐与算法参数)。
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文密码与 bcrypt 哈希是否匹配。

    Args:
        plain: 用户输入的明文密码。
        hashed: 数据库存储的 bcrypt 哈希。

    Returns:
        匹配返回 True,否则 False。
    """
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(
    data: dict[str, Any],
    secret: str,
    expires_minutes: int,
    algorithm: str = "HS256",
) -> str:
    """生成签名的 JWT 令牌。

    过期时间使用 UTC 时间写入 ``exp`` 声明,符合 JWT 协议要求,避免本地时区导致的判定偏差。

    Args:
        data: 写入 token 的业务字段(user_id、role 等),函数内部会复制后再追加 exp,不会污染入参。
        secret: 用于签名的密钥,应来自环境变量。
        expires_minutes: 过期时间偏移(分钟),从当前 UTC 时刻起算。
        algorithm: JWT 签名算法,默认 HS256。

    Returns:
        编码后的 JWT 字符串。
    """
    to_encode = data.copy()
    expire = dt.utc_now() + timedelta(minutes=expires_minutes)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, secret, algorithm=algorithm)


def decode_token(
    token: str,
    secret: str,
    algorithm: str = "HS256",
) -> dict[str, Any] | None:
    """解析并校验 JWT 令牌。

    失败场景(签名错误、格式非法、已过期)统一返回 None,调用方按业务需要抛异常,
    避免在此处耦合具体的 HTTP 状态码或异常体系。

    Args:
        token: 待校验的 JWT 字符串。
        secret: 与签发时一致的密钥。
        algorithm: 与签发时一致的算法,默认 HS256。

    Returns:
        校验成功返回 payload 字典;否则返回 None。
    """
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except JWTError:
        return None
