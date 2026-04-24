"""健康检查路由工厂 — 只探活,不探依赖。

设计取舍:
    端点**只**报告进程是否存活(liveness),不连接 PostgreSQL / Redis 等依赖。
    理由是健康端点通常对公网开放,若内置 readiness / dependency check,攻击者
    可以用低频高并发请求放大到数据库/缓存层,变成 DoS 放大器。

    需要 readiness 语义的业务(如 k8s readinessProbe)应在业务项目里自行实现,
    并把该端点限制在内网或挂鉴权。
"""

from fastapi import APIRouter

from dwyeapi.response import ApiResponse


def create_health_router(
    *,
    service_name: str,
    version: str,
    path: str = "/health",
    include_in_schema: bool = True,
) -> APIRouter:
    """构造只探活的健康检查路由。

    返回的 router 仅挂 1 个 ``GET {path}`` 端点,响应 ``ApiResponse[dict]`` 信封,
    载荷为 ``{"service": service_name, "version": version, "status": "alive"}``。

    Args:
        service_name: 服务名,通常取自业务 ``Settings.service_name``。
        version: 服务版本号,通常取自业务包 ``__version__`` 或 ``pyproject.toml``。
        path: 端点路径,默认 ``"/health"``。业务可改为 ``"/api/healthz"`` 等。
        include_in_schema: 是否在 OpenAPI 文档暴露,默认 ``True``。内网专用时可设 ``False``。

    Returns:
        已挂载端点的 ``APIRouter`` 实例,业务项目 ``app.include_router(router)`` 即可。
    """
    router = APIRouter(tags=["health"])

    @router.get(
        path,
        response_model=ApiResponse[dict],
        include_in_schema=include_in_schema,
        summary="进程存活检查",
    )
    async def liveness() -> ApiResponse[dict]:
        """返回进程存活标志及服务元信息,不触达任何外部依赖。"""
        return ApiResponse.ok(
            {
                "service": service_name,
                "version": version,
                "status": "alive",
            }
        )

    return router
