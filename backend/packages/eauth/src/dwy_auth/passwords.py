"""共享 bcrypt 实现；输入策略由认证入口验证，兼容既有 bcrypt 散列。"""

import bcrypt


def hash_password(password: str) -> str:
    """使用 bcrypt 随机盐生成散列；调用方必须先检查 72 字节上限。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """验证存量 bcrypt 散列；不截断明文，不更改历史算法。"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
