"""异常处理器注册 -- 统一响应信封 {code, message, data, timestamp}。"""

from fastapi import FastAPI


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。

    优先复用 dwyeapi 的 handler;若需追加项目特有异常(如 426 UpgradeRequired),
    在本函数内 `@app.exception_handler(MyError)` 追加。
    """
    try:
        from dwyeapi.exceptions import register_handlers

        register_handlers(app)
    except ImportError:
        # dwyeapi 未提供 register_handlers 时的最简兜底
        from fastapi import Request
        from fastapi.responses import JSONResponse

        @app.exception_handler(Exception)
        async def _fallback_handler(request: Request, exc: Exception) -> JSONResponse:
            return JSONResponse(
                status_code=500,
                content={"code": "INTERNAL_ERROR", "message": str(exc), "data": None},
            )
