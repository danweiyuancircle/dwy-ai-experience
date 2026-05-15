"""业务包配置 -- 由装配层 Settings 嵌入。"""

from pydantic import BaseModel


class DomainConfig(BaseModel):
    """业务包配置。在此追加包特有字段(如 max_records / cache_ttl 等)。"""

    enabled: bool = True
