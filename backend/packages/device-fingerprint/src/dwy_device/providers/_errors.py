"""适配器内部只传播安全错误码, 不向公开结果泄露宿主信息。"""

from ..models import DeviceErrorCode


class CollectionError(Exception):
    """预期采集失败; 禁止把原始身份、命令输出或底层错误文本作为参数。"""

    def __init__(self, code: DeviceErrorCode) -> None:
        self.code = code
        super().__init__(code.value)
