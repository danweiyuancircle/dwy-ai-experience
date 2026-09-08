"""邮箱规范化.

Gmail / Googlemail 把 plus 别名和点号视为同一收件箱;其它域名只做大小写折叠.
查重、发码 Redis key、登录查找必须走规范化结果,否则同一邮箱可开多个号.
"""

# Gmail 把 googlemail.com 当成 gmail.com 的别名,必须折到同一域名.
GMAIL_DOMAINS = frozenset({"gmail.com", "googlemail.com"})


def canonicalize_email(email: str) -> str:
    """把邮箱折成唯一收件箱标识.

    Args:
        email: 用户输入的邮箱.长度建议 [3, 254].示例:``Bai.Wen+1@Gmail.com``.

    Returns:
        规范化邮箱.Gmail 示例:``baiwen@gmail.com``;其它域名仅 lower.
        无 ``@`` 时返回 strip + lower,不抛异常,交给上游格式校验.
    """
    normalized = email.strip().lower()
    if "@" not in normalized:
        return normalized
    local, domain = normalized.rsplit("@", 1)
    if domain in GMAIL_DOMAINS:
        local = local.split("+", 1)[0].replace(".", "")
        domain = "gmail.com"
    return f"{local}@{domain}"


def is_folded_alias(email: str) -> bool:
    """输入是否因 Gmail 点号 / plus / googlemail 被折叠.

    Args:
        email: 用户输入.示例:``a+shop@gmail.com``.

    Returns:
        True 表示与规范化结果不同,应按同一收件箱处理.
        仅大小写差异不算折叠(``A@gmail.com`` -> False).
    """
    return canonicalize_email(email) != email.strip().lower()
