"""支付流水用到的稳定字面量。"""

import re

# 渠道事实。refund 表示这笔流水已经向渠道退过,金额看 refunded_fen,不是退款申请单。
STATUS_PENDING = "pending"
STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_REFUND = "refund"

CHANNEL_WECHAT = "wechat"
CHANNEL_ALIPAY = "alipay"
# 订单码与微信 Native 一样是主扫。入账只认这一类,避免把别的交易类型标成功。
CHANNELS = frozenset({CHANNEL_WECHAT, CHANNEL_ALIPAY})

# 微信成功通知的事件名与交易类型。其它值不当成功。
EVENT_TRANSACTION_SUCCESS = "TRANSACTION.SUCCESS"
# 查单不是回调。适配器把查单结果标成这个事件,入账仍看 trade_state。
EVENT_QUERY = "QUERY"
TRADE_TYPE_NATIVE = "NATIVE"
TRADE_STATE_SUCCESS = "SUCCESS"

# 账单和订单列表补查待支付单的上限。连点购买会留下多笔未支付,一次打开页面不能打出几十次查单。
PENDING_PULL_LIMIT = 20

# 商户订单号:微信要求 6–32,字符集数字字母及 _-|*。uuid4().hex 正好 32。
ORDER_NO_MIN_LEN = 6
ORDER_NO_MAX_LEN = 32
ORDER_NO_RE = re.compile(rf"^[0-9A-Za-z_|\-*]{{{ORDER_NO_MIN_LEN},{ORDER_NO_MAX_LEN}}}$")

# 渠道交易号列宽。微信单号经常也落在商户订单号字符集里,搜索时要能分开查。
CHANNEL_TRADE_NO_MAX_LEN = 64

# 调用方用户标识只作回对,不解释成某张用户表的主键。
USER_ID_MAX_LEN = 64

# 金额单位分。微信 Native 金额为整数分,这里卡在 1 分到 1e8 分(100 万元)。
AMOUNT_FEN_MIN = 1
AMOUNT_FEN_MAX = 100_000_000

# 商品描述上限来自微信 Native 字段长度。
DESCRIPTION_MAX_LEN = 127

# 验签探测:微信用此前缀打探测流量,必须当验签失败,不能当支付成功。
SIGNTEST_PREFIX = "WECHATPAY/SIGNTEST/"
