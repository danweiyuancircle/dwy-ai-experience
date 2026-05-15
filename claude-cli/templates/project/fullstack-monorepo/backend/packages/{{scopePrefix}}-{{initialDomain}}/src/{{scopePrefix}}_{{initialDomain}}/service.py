"""业务逻辑层。

依赖通过 `__init__.py` 的 get_config() 拿配置,通过 get_provider() 拿外部服务。
不在 service 里 import app.* / FastAPI 相关,保持纯业务无 web 框架耦合。
"""


class DomainService:
    """业务服务 stub -- 在此实现具体业务方法。"""

    pass
