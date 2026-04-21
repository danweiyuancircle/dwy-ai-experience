"""PII 数据脱敏工具。

纯函数模块,提供一组统一的个人敏感信息脱敏函数。所有公开函数接收 ``str`` 返回脱敏后的 ``str``,
输入不合法或为空时原样返回,不抛异常,调用方无需额外做防御性判断。
"""

import re

# ---------------------------------------------------------------------------
# 内部常量
# ---------------------------------------------------------------------------

_PHONE_RE = re.compile(r"^\d{11}$")
_EMAIL_RE = re.compile(r"^([^@]+)@([^@]+)$")
_ID_CARD_RE = re.compile(r"^\d{17}[\dXx]$")
_BANK_CARD_RE = re.compile(r"^\d{13,19}$")
_IPV4_RE = re.compile(r"^(\d{1,3}\.\d{1,3}\.\d{1,3})\.\d{1,3}$")
_ADDRESS_RE = re.compile(r"^(.*(?:省|自治区|市|区|县|镇|旗))")


# ---------------------------------------------------------------------------
# 公开函数
# ---------------------------------------------------------------------------


def mask_phone(value: str) -> str:
    """脱敏 11 位手机号,保留前 3 后 4 位,示例:138****5678。"""
    if not _PHONE_RE.match(value):
        return value
    return value[:3] + "****" + value[7:]


def mask_email(value: str) -> str:
    """脱敏邮箱,保留首字母和域名,示例:z***@gmail.com。"""
    if not value:
        return value
    match = _EMAIL_RE.match(value)
    if not match:
        return value
    local, domain = match.group(1), match.group(2)
    return local[0] + "***@" + domain


def mask_id_card(value: str) -> str:
    """脱敏 18 位身份证号,保留前 3 后 4 位,示例:420***********1234。"""
    if not _ID_CARD_RE.match(value):
        return value
    return value[:3] + "***********" + value[14:]


def mask_bank_card(value: str) -> str:
    """脱敏银行卡号,保留前 4 后 4 位,示例:6222********1234。"""
    if not _BANK_CARD_RE.match(value):
        return value
    middle_len = len(value) - 8
    return value[:4] + "*" * middle_len + value[-4:]


def mask_name(value: str) -> str:
    """脱敏中文姓名,示例:张*明(两字姓名保留姓)。"""
    if len(value) <= 1:
        return value
    if len(value) == 2:
        return value[0] + "*"
    return value[0] + "*" * (len(value) - 2) + value[-1]


def mask_address(value: str) -> str:
    """脱敏地址,保留到省/市/区/县级行政单位,示例:浙江省杭州市西湖区****。

    未匹配到行政区后缀时退化为保留前 6 个字符。
    """
    if not value:
        return value
    match = _ADDRESS_RE.match(value)
    if match:
        return match.group(1) + "****"
    if len(value) <= 6:
        return value
    return value[:6] + "****"


def mask_ip(value: str) -> str:
    """脱敏 IPv4 地址,保留前三段,示例:192.168.1.*。"""
    if not value:
        return value
    match = _IPV4_RE.match(value)
    if not match:
        return value
    return match.group(1) + ".*"


def mask_license_plate(value: str) -> str:
    """脱敏车牌号,保留省份简称+字母与末位,示例:浙A***8。"""
    if len(value) < 7:
        return value
    return value[:2] + "***" + value[-1]


def mask_text(text: str, start: int = 1, end: int = 1, mask_char: str = "*") -> str:
    """通用文本脱敏:保留前 ``start`` 与后 ``end`` 个字符,中间用 ``mask_char`` 替代。

    当 ``start + end`` 大于等于文本长度时原样返回,避免因脱敏导致明文全部暴露(保留过少)或无法识别。

    Args:
        text: 原始文本。
        start: 保留头部的字符数,默认 1。
        end: 保留尾部的字符数,默认 1;为 0 时仅保留头部。
        mask_char: 用于替换中间部分的字符,默认 ``*``。

    Returns:
        脱敏后的字符串;空文本或保留长度超界时原样返回。
    """
    if not text:
        return text
    if start + end >= len(text):
        return text
    middle = mask_char * (len(text) - start - end)
    if end > 0:
        return text[:start] + middle + text[len(text) - end :]
    return text[:start] + middle
