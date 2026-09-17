"""邮箱规范化与常见域名白名单.

Gmail / Googlemail 把 plus 别名和点号视为同一收件箱;其它域名只做大小写折叠.
查重、发码 Redis key、登录查找必须走规范化结果,否则同一邮箱可开多个号.

一次性邮箱会轮换马甲域(如 mail.tm 的 uberip.com),社区黑名单跟不上.
``send_code`` 默认走 ``require_common_email_domain``;B2B 设 ``EMAIL__REQUIRE_COMMON_DOMAIN=false``.
机构域用 ``EMAIL__EXTRA_ALLOW_DOMAINS``,不要把公司域写进 ``COMMON_EMAIL_DOMAINS``.
"""

from collections.abc import Collection, Iterable

from dwyeapi.exceptions import BusinessError

# Gmail 把 googlemail.com 当成 gmail.com 的别名,必须折到同一域名.
GMAIL_DOMAINS = frozenset({"gmail.com", "googlemail.com"})

# 常见个人邮箱域名.只做精确匹配,不把 mail.qq.com 当成 qq.com.
# 机构 / 高校(非 edu.cn)走 extra_allow,不要把公司域写进这张表.
COMMON_EMAIL_DOMAINS = frozenset(
    {
        "qq.com",
        "foxmail.com",
        "vip.qq.com",
        "163.com",
        "126.com",
        "yeah.net",
        "vip.163.com",
        "vip.126.com",
        "188.com",
        "sina.com",
        "sina.cn",
        "vip.sina.com",
        "sohu.com",
        "139.com",
        "189.cn",
        "21cn.com",
        "aliyun.com",
        "tom.com",
        "263.net",
        "gmail.com",
        "googlemail.com",
        "outlook.com",
        "hotmail.com",
        "live.com",
        "live.cn",
        "msn.com",
        "icloud.com",
        "me.com",
        "mac.com",
        "proton.me",
        "protonmail.com",
        "yahoo.com",
        "ymail.com",
    }
)

_EDU_CN_SUFFIX = ".edu.cn"
_EDU_CN_DOMAIN = "edu.cn"
_EMAIL_DOMAIN_NOT_ALLOWED_CODE = "EMAIL_DOMAIN_NOT_ALLOWED"
_EMAIL_DOMAIN_NOT_ALLOWED_MESSAGE = "请使用常用邮箱注册"


def canonicalize_email(email: str) -> str:
    """把邮箱折成唯一收件箱标识.

    Args:
        email (str): 用户输入的邮箱.长度建议 ``[3, 254]``.示例:``Bai.Wen+1@Gmail.com``.

    Returns:
        str: 规范化邮箱.Gmail 示例:``baiwen@gmail.com``;其它域名仅 lower.
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
        email (str): 用户输入.示例:``a+shop@gmail.com``.

    Returns:
        bool: True 表示与规范化结果不同,应按同一收件箱处理.
        仅大小写差异不算折叠(``A@gmail.com`` -> False).
    """
    return canonicalize_email(email) != email.strip().lower()


def is_common_email_domain(
    email: str,
    *,
    extra_allow: Collection[str] = (),
    allow_edu_cn: bool = True,
) -> bool:
    """邮箱域名是否在常见个人邮箱白名单.

    先 ``canonicalize_email``,再精确匹配域名.``mail.qq.com`` 不等于 ``qq.com``.
    ``allow_edu_cn`` 只认 ``edu.cn`` / ``*.edu.cn``,不放行 ``columbia.edu`` 这类任意 ``.edu``.

    Args:
        email (str): 用户输入的邮箱.长度建议 ``[3, 254]``.示例:``user@qq.com``.
        extra_allow (Collection[str]): 业务追加的域名或完整邮箱,大小写不敏感.
            默认空.示例:``{"yanbofund.com"}``.
        allow_edu_cn (bool): 是否放行中国高校域.默认 ``True``.示例:``False``.

    Returns:
        bool: 在白名单或 extra_allow / edu.cn 规则内为 True;无 ``@`` 为 False.
    """
    domain = _email_domain(email)
    if not domain:
        return False
    if domain in COMMON_EMAIL_DOMAINS:
        return True
    if domain in _normalize_allow_domains(extra_allow):
        return True
    return allow_edu_cn and _is_edu_cn(domain)


def require_common_email_domain(
    email: str,
    *,
    extra_allow: Collection[str] = (),
    allow_edu_cn: bool = True,
) -> str:
    """校验常见邮箱域名,通过则返回规范化地址.

    ``send_code`` 在 ``require_common_domain=True``(默认)时调用.
    失败抛 ``BusinessError``,消息不回显用户输入.

    Args:
        email (str): 用户输入的邮箱.长度建议 ``[3, 254]``.示例:``user@163.com``.
        extra_allow (Collection[str]): 业务追加的域名或完整邮箱.默认空.示例:``{"contek.io"}``.
        allow_edu_cn (bool): 是否放行 ``*.edu.cn``.默认 ``True``.示例:``True``.

    Returns:
        str: 规范化邮箱.示例:``baiwen@gmail.com``.

    Raises:
        BusinessError: 域名不在白名单.``code`` 为 ``EMAIL_DOMAIN_NOT_ALLOWED``.
    """
    if not is_common_email_domain(email, extra_allow=extra_allow, allow_edu_cn=allow_edu_cn):
        raise BusinessError(message=_EMAIL_DOMAIN_NOT_ALLOWED_MESSAGE, code=_EMAIL_DOMAIN_NOT_ALLOWED_CODE)
    return canonicalize_email(email)


def _email_domain(email: str) -> str:
    """取出规范化后的域名;无 ``@`` 返回空串.

    Args:
        email (str): 用户输入.示例:``User@QQ.com``.

    Returns:
        str: 小写域名.示例:``qq.com``;非法输入为 ``""``.
    """
    canonical = canonicalize_email(email)
    if "@" not in canonical:
        return ""
    return canonical.rsplit("@", 1)[1]


def _normalize_allow_domains(items: Iterable[str]) -> set[str]:
    """把 extra_allow 折成小写域名集合.

    条目可以是 ``company.example`` 或 ``ops@example.com``.空串丢弃.

    Args:
        items (Iterable[str]): 业务传入的域名或邮箱.示例:``{"ops@example.com"}``.

    Returns:
        set[str]: 小写域名.示例:``{"contek.io"}``.
    """
    domains: set[str] = set()
    for item in items:
        value = item.strip().lower()
        if not value:
            continue
        if "@" in value:
            value = value.rsplit("@", 1)[1]
        if value:
            domains.add(value)
    return domains


def _is_edu_cn(domain: str) -> bool:
    """是否中国高校域名.

    只认 ``edu.cn`` 与 ``*.edu.cn``,避免 ``atlas.edu.kg`` 一类假教育域.

    Args:
        domain (str): 已小写的域名.示例:``mails.tsinghua.edu.cn``.

    Returns:
        bool: 是 ``edu.cn`` 后缀则为 True.
    """
    return domain == _EDU_CN_DOMAIN or domain.endswith(_EDU_CN_SUFFIX)
