"""Email Provider 基类 -- 封装 Redis 验证码存取 + 品牌化 HTML/text 渲染。"""

import secrets
from abc import ABC, abstractmethod
from collections.abc import Collection
from html import escape
from typing import Literal

import redis.asyncio as aioredis

from dwyeapi.cache import get_redis
from dwyeapi.email import canonicalize_email, require_common_email_domain

CODE_KEY_PREFIX = "dwyeapi:email:code:"
DEFAULT_CODE_TTL = 300
DEFAULT_CODE_LENGTH = 6


class EmailProviderBase(ABC):
    """Email Provider 抽象基类。

    共享验证码生成 + Redis 存取 + 一次性校验逻辑;子类只实现 `_send()` 发送动作。
    同时提供 `_render_code_html()` / `_render_code_text()` 让所有子类共用同一套品牌化模板。
    """

    def __init__(
        self,
        code_ttl: int = DEFAULT_CODE_TTL,
        code_length: int = DEFAULT_CODE_LENGTH,
        brand_name: str = "",
        brand_tagline: str = "",
        brand_url: str = "",
        brand_slogan: str = "",
        support_email: str = "",
        redis: aioredis.Redis | None = None,
        require_common_domain: bool = True,
        extra_allow_domains: Collection[str] = (),
        allow_edu: bool = True,
        allow_edu_cn: bool = True,
        *,
        brand_tagline_en: str = "",
        brand_slogan_en: str = "",
    ) -> None:
        """初始化。

        Args:
            code_ttl: 验证码有效期(秒),默认 300。
            code_length: 验证码位数,默认 6。
            brand_name: 品牌名,展示在邮件页眉与页脚版权;空串走通用模板。
            brand_tagline: 品牌副标语(英文/口号),展示在页眉右上;空串则不显示。
            brand_url: 品牌官网,展示在页脚链接;空串则不显示。
            brand_slogan: 页脚版权下方一行说明文案;空串则不显示。
            support_email: 客服邮箱,展示在邮件正文底部;空串则不显示。
            redis: 可选显式注入的 Redis 连接;为 None 时 fallback 到 dwyeapi.cache.get_redis()。
            require_common_domain: 发码前是否校验常见邮箱域名.默认 True.C 端保持开启.
            extra_allow_domains: 额外放行域名.默认空.示例:``("chances.com.cn",)``.
            allow_edu: 是否放行美国 ``.edu``.默认 True.
            allow_edu_cn: 是否放行 ``*.edu.cn``.默认 True.
            brand_tagline_en: 英文邮件的品牌副标语;空串时省略,不复用中文配置。
            brand_slogan_en: 英文邮件的页脚说明;空串时省略,不复用中文配置。
        """
        self._ttl = code_ttl
        self._length = code_length
        self._brand_name = brand_name
        self._brand_tagline = brand_tagline
        self._brand_url = brand_url
        self._brand_slogan = brand_slogan
        self._brand_tagline_en = brand_tagline_en
        self._brand_slogan_en = brand_slogan_en
        self._support_email = support_email
        self._redis = redis
        self._require_common_domain = require_common_domain
        self._extra_allow = tuple(extra_allow_domains)
        self._allow_edu = allow_edu
        self._allow_edu_cn = allow_edu_cn

    async def _get_redis(self) -> aioredis.Redis:
        """获取 Redis 连接,优先使用注入的,否则取全局单例。"""
        if self._redis is not None:
            return self._redis
        return await get_redis()

    def _generate_code(self) -> str:
        """生成指定位数的数字验证码。"""
        return "".join(secrets.choice("0123456789") for _ in range(self._length))

    def _code_key(self, target: str) -> str:
        """验证码 Redis key.Gmail plus/点号/googlemail 折成同一收件箱,避免别名绕过."""
        return f"{CODE_KEY_PREFIX}{canonicalize_email(target)}"

    async def send_verification_code(self, target: str, code: str, *, language: Literal["zh", "en"] = "en") -> bool:
        """只交付调用方生成的验证码,不访问Redis;调用方必须负责限流、存储和原子核销。

        供数据库事务验证码系统复用现有品牌模板与邮件通道。验证码生命周期与模板TTL需由宿主保持一致。
        language 由 HTTP 边界归一化,逐次传入;未指定时发送英文。
        """
        if self._require_common_domain:
            require_common_email_domain(
                target,
                extra_allow=self._extra_allow,
                allow_edu=self._allow_edu,
                allow_edu_cn=self._allow_edu_cn,
            )
        return await self._send(target.strip(), code, language=language)

    async def send_code(self, target: str, *, language: Literal["zh", "en"] = "en") -> bool:
        """生成验证码:先校验域名,发送成功再写入 Redis.

        顺序约束:域名不在白名单时抛 ``BusinessError``,不发信、不落库.
        ``_send`` 失败时不落库,避免用户未收到邮件却有可校验码.
        发送成功后写 Redis;若写库失败则返回 False(邮件已发出属极端边界,业务可重发覆盖).
        发信信封用用户输入的地址;Redis key 走 ``canonicalize_email``,Gmail 别名共用同一码.
        language 仅控制本次邮件,默认英文,不影响验证码存储与核销。
        """
        if self._require_common_domain:
            require_common_email_domain(
                target,
                extra_allow=self._extra_allow,
                allow_edu=self._allow_edu,
                allow_edu_cn=self._allow_edu_cn,
            )
        code = self._generate_code()
        deliver_to = target.strip()
        if not await self._send(deliver_to, code, language=language):
            return False
        redis = await self._get_redis()
        await redis.set(self._code_key(target), code, ex=self._ttl)
        return True

    async def verify_code(self, target: str, code: str) -> bool:
        """从 Redis 读取存储的验证码比对,成功则删除 key(一次性).

        ``target`` 经 ``canonicalize_email`` 后再查 key,与 ``send_code`` 对齐.
        """
        redis = await self._get_redis()
        key = self._code_key(target)
        stored = await redis.get(key)
        if stored is None:
            return False
        stored_str = stored if isinstance(stored, str) else stored.decode()
        if stored_str != code:
            return False
        await redis.delete(key)
        return True

    def _render_code_html(self, code: str, *, language: Literal["zh", "en"] = "en") -> str:
        """渲染品牌化验证码 HTML 邮件 -- 主流邮件客户端兼容的 inline CSS 模板。

        使用 table 布局 + inline style,适配 Gmail / Outlook / 163 / QQ / Apple Mail。
        所有动态文案经 `html.escape` 转义,避免 brand_name 含特殊字符时破坏结构。
        """
        minutes = max(self._ttl // 60, 1)
        chinese = language == "zh"
        html_language = "zh-CN" if chinese else "en"
        title = "验证码" if chinese else "Verification code"
        heading = "您正在进行身份验证" if chinese else "Verify your identity"
        brand = escape(self._brand_name) or ("验证码" if chinese else "Account security")
        tagline = escape(self._brand_tagline if chinese else self._brand_tagline_en)
        url = escape(self._brand_url)
        slogan = escape(self._brand_slogan if chinese else self._brand_slogan_en)
        support = escape(self._support_email)
        code_safe = escape(code)
        introduction = (
            f'您好,请使用以下验证码完成本次操作。该验证码 <strong style="color:#0f172a;">{minutes} 分钟内有效</strong>,请勿向任何人泄露。'
            if chinese
            else f'Use the verification code below to complete your request. It is valid for <strong style="color:#0f172a;">{minutes} minutes</strong>. Do not share it with anyone.'
        )
        ignore_notice = (
            "若非本人操作,请忽略此邮件,您的账户依然安全。"
            if chinese
            else "If you did not request this code, you can safely ignore this email. Your account is still secure."
        )
        reply_notice = (
            "本邮件由系统自动发送,请勿直接回复。"
            if chinese
            else "This email was sent automatically. Please do not reply."
        )
        support_notice = "如有疑问,请联系客服:" if chinese else "If you need help, contact support: "

        header_right = (
            f'<td align="right" style="color:#94a3b8;font-size:13px;letter-spacing:1px;">{tagline}</td>'
            if tagline
            else ""
        )
        support_block = (
            f'<p style="margin:0 0 8px 0;color:#475569;font-size:13px;line-height:1.7;">'
            f"{support_notice}"
            f'<a href="mailto:{support}" style="color:#1e3a8a;text-decoration:none;">{support}</a>'
            "</p>"
            if support
            else ""
        )
        slogan_block = f"<br/>{slogan}" if slogan else ""
        footer_link = (
            f'<a href="{url}" style="color:#1e3a8a;text-decoration:none;font-weight:500;">'
            f"{url.replace('https://', '').replace('http://', '')} →"
            "</a>"
            if url
            else ""
        )

        return f"""<!DOCTYPE html>
<html lang="{html_language}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{brand} {title}</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6fa;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;-webkit-font-smoothing:antialiased;">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f4f6fa;padding:40px 16px;">
  <tr><td align="center">
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="560" style="max-width:560px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(15,23,42,0.06);">
      <tr>
        <td style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:32px 40px;">
          <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
            <tr>
              <td style="color:#ffffff;font-size:20px;font-weight:600;letter-spacing:1px;">{brand}</td>
              {header_right}
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td style="padding:40px 40px 8px 40px;">
          <h1 style="margin:0 0 12px 0;color:#0f172a;font-size:22px;font-weight:600;line-height:1.4;">{heading}</h1>
          <p style="margin:0 0 28px 0;color:#475569;font-size:14px;line-height:1.7;">
            {introduction}
          </p>
          <div style="margin:0 0 28px 0;background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:24px;text-align:center;">
            <div style="color:#64748b;font-size:12px;letter-spacing:2px;margin-bottom:12px;">VERIFICATION CODE</div>
            <div style="color:#0f172a;font-size:36px;font-weight:700;letter-spacing:10px;font-family:'SF Mono','Menlo','Consolas',monospace;">{code_safe}</div>
          </div>
          <p style="margin:0 0 8px 0;color:#475569;font-size:13px;line-height:1.7;">{ignore_notice}</p>
          {support_block}
          <p style="margin:0;color:#94a3b8;font-size:12px;line-height:1.7;">{reply_notice}</p>
        </td>
      </tr>
      <tr>
        <td style="padding:24px 40px 32px 40px;border-top:1px solid #f1f5f9;">
          <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
            <tr>
              <td style="color:#94a3b8;font-size:12px;line-height:1.6;">© {brand}{slogan_block}</td>
              <td align="right" style="color:#94a3b8;font-size:12px;">{footer_link}</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </td></tr>
</table>
</body>
</html>"""

    def _render_code_text(self, code: str, *, language: Literal["zh", "en"] = "en") -> str:
        """渲染纯文本备份 -- 给不支持 HTML 的客户端,同时降低被反垃圾误判的概率。"""
        minutes = max(self._ttl // 60, 1)
        chinese = language == "zh"
        brand = self._brand_name or ("验证码" if chinese else "Account security")
        lines = (
            [
                f"【{brand}】您正在进行身份验证。",
                "",
                f"您的验证码是:{code},{minutes} 分钟内有效,请勿向任何人泄露。",
                "",
                "若非本人操作,请忽略此邮件。",
            ]
            if chinese
            else [
                f"[{brand}] Verify your identity.",
                "",
                f"Your verification code is: {code}. It is valid for {minutes} minutes. Do not share it with anyone.",
                "",
                "If you did not request this code, you can safely ignore this email.",
            ]
        )
        if self._support_email:
            notice = "如有疑问,请联系客服:" if chinese else "If you need help, contact support: "
            lines.append(f"{notice}{self._support_email}")
        if self._brand_url:
            lines.append(f"— {self._brand_name or ''} {self._brand_url}".strip())
        return "\n".join(lines)

    @abstractmethod
    async def _send(self, target: str, code: str, *, language: Literal["zh", "en"] = "en") -> bool:
        """子类实现发送动作;language 逐次透传给模板,不得写入实例状态。"""
        ...
