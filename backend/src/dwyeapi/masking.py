"""PII data masking utilities.

Pure-function module for standardised personal data masking.  Every
public function accepts a ``str`` and returns the masked ``str``.
Invalid or empty inputs are returned unchanged — no exceptions raised.
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
    """138****5678"""
    if not _PHONE_RE.match(value):
        return value
    return value[:3] + "****" + value[7:]


def mask_email(value: str) -> str:
    """z***@gmail.com"""
    if not value:
        return value
    match = _EMAIL_RE.match(value)
    if not match:
        return value
    local, domain = match.group(1), match.group(2)
    return local[0] + "***@" + domain


def mask_id_card(value: str) -> str:
    """420***********1234"""
    if not _ID_CARD_RE.match(value):
        return value
    return value[:3] + "***********" + value[14:]


def mask_bank_card(value: str) -> str:
    """6222********1234"""
    if not _BANK_CARD_RE.match(value):
        return value
    middle_len = len(value) - 8
    return value[:4] + "*" * middle_len + value[-4:]


def mask_name(value: str) -> str:
    """张*明"""
    if len(value) <= 1:
        return value
    if len(value) == 2:
        return value[0] + "*"
    return value[0] + "*" * (len(value) - 2) + value[-1]


def mask_address(value: str) -> str:
    """浙江省杭州市西湖区****"""
    if not value:
        return value
    match = _ADDRESS_RE.match(value)
    if match:
        return match.group(1) + "****"
    if len(value) <= 6:
        return value
    return value[:6] + "****"


def mask_ip(value: str) -> str:
    """192.168.1.*"""
    if not value:
        return value
    match = _IPV4_RE.match(value)
    if not match:
        return value
    return match.group(1) + ".*"


def mask_license_plate(value: str) -> str:
    """浙A***8"""
    if len(value) < 7:
        return value
    return value[:2] + "***" + value[-1]


def mask_text(text: str, start: int = 1, end: int = 1, mask_char: str = "*") -> str:
    """Keep first *start* and last *end* chars, mask the rest."""
    if not text:
        return text
    if start + end >= len(text):
        return text
    middle = mask_char * (len(text) - start - end)
    if end > 0:
        return text[:start] + middle + text[len(text) - end :]
    return text[:start] + middle
