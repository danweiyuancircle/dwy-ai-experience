# 时间

业务时间统一中国时区。**禁止 `datetime.now()` / `datetime.utcnow()`**，走 `dwyeapi.dt`。

- `dt.now()`：naive（Asia/Shanghai），数据库存储
- `dt.utc_now()`：aware UTC，JWT exp 等协议字段
- 两者不能混用
