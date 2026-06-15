"""Pydantic Request/Response models。"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str
    domain: str


# 在此追加业务 schema:
# class CreateItemRequest(BaseModel):
#     name: str
#     ...
#
# class ItemResponse(BaseModel):
#     id: int
#     name: str
#     ...
