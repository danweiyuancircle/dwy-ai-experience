---
source_url: https://docs.dolphindb.cn/zh/plugins/mqtt5.html
fetched_at: 2026-05-19T09:46:12Z
category: plugins
title: mqtt5
sha1: f066ffad0b8f78499be8e6bf069bb76046911849
---

# mqtt5

mqtt5 插件基于 Paho MQTT C 库开发，用于与 MQTT 服务器建立连接并进行交互。
插件支持连接管理、消息发布与订阅、加密通信等功能，使开发者能够专注于应用逻辑而无需担心底层通信细节。 区别于原有的 [mqtt](mqtt/mqtt.html) 插件，mqtt5 插件支持 MQTT 5.0 协议和加密通信功能。

## 安装插件

### 版本要求

DolphinDB Server：2.00.17、2.00.18、3.00.5 及更高版本，且部署于 Linux x86-64 系统。

### 安装步骤

1. 在 DolphinDB 客户端中使用 [listRemotePlugins](../funcs/l/listRemotePlugins.html) 函数查看可供安装的插件。

   ```dolphindb
   login("admin", "123456")
   listRemotePlugins()
   ```
2. 使用 [installPlugin](../funcs/i/installPlugin.html)
   函数安装插件。

   ```dolphindb
   installPlugin("mqtt5")
   ```
3. 使用 [loadPlugin](../funcs/l/loadPlugin.html) 函数加载插件。

   ```dolphindb
   loadPlugin("mqtt5")
   ```

## 接口说明

### connect

**语法**

```dolphindb
mqtt5::connect(uri, [config])
```

**详情**

建立与 MQTT 服务器的连接并返回一个连接句柄。 会话结束时自动关闭连接，也可以主动调用 `close` 函数关闭连接。

**参数**

**uri** STRING 类型标量，指定要连接的 MQTT 服务器的 URI 地址，格式为 protocol://host:port。

- protocol 为连接协议，可选值如下：

  - tcp 或 mqtt：表示非安全的 TCP； 如果省略 protocol，等价于填入 tcp 或 mqtt。
  - ssl、tls 或 mqtts：表示加密的 SSL/TLS。
  - ws：表示非安全的 WebSocket。
  - wss：表示安全的 WebSocket。
- host 为 MQTT 服务器的主机名； port 为端口号，可以省略，省略时自动填入连接协议对应的默认值。
- 如果使用不加密的协议，*config*里和 SSL 有关的配置项不会生效。

**config** 可选参数，一个字典，用于设置配置项。 键为 STRING 类型标量，值为 ANY。

- “qos”：INT 类型标量，指定发布者与订阅者之间消息传递的保证级别。

  - 0（默认值）：最多交付一次。 “发后即忘”，消息可能丢失，不重传。
  - 1：至少交付一次。 保证消息送达，但可能因网络确认包丢失而导致重复。
  - 2：只交付一次。 确保消息既不丢失也不重复。
- “username”：STRING 类型标量，指定用于登录 MQTT 服务器的用户名。 默认为空。
- “password”：STRING 类型标量，指定用于登录 MQTT 服务器的密码。 只有设置了 username 时才会生效。 默认为空。
- “clientID”：STRING 类型标量，指定连接的 ID，不指定则自动生成。 如果已存在某个 clientID 对应的连接，指定相同的 clientID 可能导致前一个连接断开，或者此次连接失败，具体行为取决于使用的 MQTT broker。
- “mqttVersion”：INT 类型标量，指定 MQTT 协议版本。

  - 0（默认值）：先尝试 3.1.1 版本，若失败则回退至 3.1 版本。
  - 3：仅尝试 3.1 版本。
  - 4：仅尝试 3.1.1 版本。
  - 5：仅尝试 5.0 版本。
- “useSSL”：BOOL 类型标量，指定是否使用 SSL 加密。 如果 protocol 设置为加密协议，比如 ssl，useSSL 必须指定为 true。 默认为 false。
- “enableServerCertAuth”：BOOL 类型标量，指定是否启用服务器证书验证。 默认为 false。
- “trustStore”：可选，STRING 类型标量，指定客户端所信任公钥数字证书的 PEM 格式文件路径。 默认为空。
- “maxBufferedMessages”：INT 类型标量，指定每个连接可缓冲的发布消息条数，默认值为 100。

**连接错误码**

| 错误码 | 原因 |
| --- | --- |
| 5 | 未授权，没有进行认证。 |
| 4 | 用户名或密码错误。 |
| 3 | 服务器不可用。 |
| 2 | 客户端标识符（clientID）被拒绝。 |
| 1 | 协议版本不可接受。 |
| 0 | 无错误，表示 MQTT 客户端操作成功完成。 |
| -1 | MQTT 客户端操作失败的通用错误。 |
| -2 | `MQTTAsync_PERSISTENCE_ERROR` 错误。 |
| -3 | 客户端已断开连接。 |
| -4 | 已达到允许同时传输中的最大消息数量限制。 |
| -5 | 检测到无效的 UTF-8 字符串。 |
| -6 | 在无效的情况下提供了 NULL 值的参数。 |
| -7 | 主题名被 NULL 字符截断，无法访问完整的主题。 |
| -8 | 结构体参数的 eyecatcher 和版本号不正确。 |
| -9 | qos 键的值不是 0、1 或 2。 |
| -10 | 所有 65535 个 MQTT 消息 ID 都正在使用中。 |
| -11 | 请求尚未完成时被丢弃。 |
| -12 | 无法缓冲更多消息。 |
| -13 | 尝试使用非 SSL 版本的库进行 SSL 连接。 |
| -14 | serverURI 中的协议前缀错误，启用 TLS 的前缀（ssl、mqtts、wss）仅在链接了 TLS 版本的库时有效。 |
| -15 | 请勿使用适用于其他 MQTT 版本的选项。 |
| -16 | 该调用不适用于客户端当前使用的 MQTT 版本。 |
| -17 | 遗嘱主题长度为 0。 |
| -18 | 连接或断开连接命令被忽略，因为队列头部已有一个连接或断开连接命令正在等待处理。 请使用 onSuccess/onFailure 回调来等待前一个连接或断开连接命令完成。 |
| -19 | 连接选项中的 maxBufferedMessages 必须 >= 0。 |

### close

**语法**

```dolphindb
mqtt5::close(conn)
```

**详情**

断开与 MQTT 服务器的连接。

**参数**

**conn** 由 `connect` 接口返回的连接句柄。

### publish

**语法**

```dolphindb
mqtt5::publish(conn,topic,obj)
```

**详情**

向 MQTT 服务器发布消息。

**参数**

**conn** 由 `connect` 接口返回的连接句柄。

**topic** STRING 类型标量，指定发布的主题。

**msg** STRING 类型标量或向量，指定发布的消息内容。

### subscribe

**语法**

```dolphindb
mqtt5::subscribe(uri, topic, handler, [config])
```

**详情**

向 MQTT 服务器订阅消息，返回一个订阅句柄。

**参数**

**uri**  STRING 类型标量，指定要连接的 MQTT 服务器的 URI 地址，格式为 protocol://host:port。

- protocol 为连接协议，可选值如下：

  - tcp 或 mqtt：表示非安全的 TCP； 如果省略 protocol，等价于填入 tcp 或 mqtt。
  - ssl、tls 或 mqtts：表示加密的 SSL/TLS。
  - ws：表示非安全的 WebSocket。
  - wss：表示安全的 WebSocket。
- host 为 MQTT 服务器的主机名； port 为端口号，可以省略，省略时自动填入连接协议对应的默认值。
- 如果使用不加密的协议，*config*里和 SSL 有关的配置项不会生效。

**topic** STRING 类型标量，指定订阅的主题。

**handler** 一个包含两个参数的自定义函数，用于处理接收到的消息。 参数为 (topic, msg)，其中 topic 为 STRING
标量，指定订阅收到消息的主题； msg 为 STRING 标量，指定订阅收到的消息。

**config** 可选参数，一个字典，用于设置配置项。 键为 STRING 类型标量，值为 ANY。

- “qos”：INT 类型标量，指定发布者与订阅者之间消息传递的保证级别。

  - 0（默认值）：最多交付一次。 “发后即忘”，消息可能丢失，不重传。
  - 1：至少交付一次。 保证消息送达，但可能因网络确认包丢失而导致重复。
  - 2：只交付一次。 确保消息既不丢失也不重复。
- “username”：STRING 类型标量，指定用于登录 MQTT 服务器的用户名。 默认为空。
- “password”：STRING 类型标量，指定用于登录 MQTT 服务器的密码。 只有设置了 username 时才会生效。 默认为空。
- “clientID”：STRING 类型标量，指定连接的 ID，不指定则自动生成。 如果已存在某个 clientID 对应的连接，指定相同的 clientID 可能导致前一个连接断开，或者此次连接失败，具体行为取决于使用的 MQTT broker。
- “mqttVersion”：INT 类型标量，指定 MQTT 协议版本。

  - 0（默认值）：先尝试 3.1.1 版本，若失败则回退至 3.1 版本。
  - 3：仅尝试 3.1 版本。
  - 4：仅尝试 3.1.1 版本。
  - 5：仅尝试 5.0 版本。
- “useSSL”：BOOL 类型标量，指定是否使用 SSL 加密。 如果 protocol 设置为加密协议，比如 ssl，useSSL 必须指定为 true。 默认为 false。
- “enableServerCertAuth”：BOOL 类型标量，指定是否启用服务器证书验证。 默认为 false。
- “trustStore”：可选，STRING 类型标量，指定客户端所信任公钥数字证书的 PEM 格式文件路径。 默认为空。

### unsubscribe

**语法**

```dolphindb
mqtt5::unsubscribe(conn)
```

**详情**

取消订阅 MQTT 服务器的消息。

**参数**

**conn** 由 `subscribe` 返回的订阅句柄或
`getSubscriberStat` 返回的订阅标识符。

### getSubscriberStat

**语法**

```dolphindb
mqtt5::getSubscriberStat()
```

**详情**

查询所有订阅信息，返回一个包含 6 列的表。

| 列名 | 含义 |
| --- | --- |
| subscriptionId | 订阅连接的标识符。 |
| user | 建立订阅的会话用户。 |
| uri | MQTT 服务器的 URI 地址。 |
| topic | 订阅的主题。 |
| createTimestamp | 订阅的建立时间。 |
| receivedPackets | 订阅收到的消息报文数。 |

## 示例

```dolphindb
loadPlugin("mqtt5")
go
// 配置项
config = dict(STRING, ANY)
config[`useSSL] = true
config[`mqttVersion] = 5
// 创建发布连接
pub_conn=mqtt5::connect("tls://broker.emqx.io:8883", config)
// 创建订阅连接
table = table(1000:0, [`topic, `message], [STRING, STRING])
def onMessage(tb, topic, payload) {
    tableInsert(tb, topic, payload)
}
sub_conn = mqtt5::subscribe("tls://broker.emqx.io:8883", "test_topic/#", onMessage{table}, config)
// 发布
mqtt5::publish(pub_conn, "test_topic/1", "MQTT test publish1")
mqtt5::publish(pub_conn, "test_topic/2", "MQTT test publish2")
mqtt5::publish(pub_conn, "test_topic/2", "MQTT test publish3")
mqtt5::publish(pub_conn, "test_topic/3", "MQTT test publish4")
mqtt5::publish(pub_conn, "test_topic/3", "MQTT test publish5")
// 查看订阅结果和状态
sleep(1000)
print table
mqtt5::getSubscriberStat()
// 关闭连接
mqtt5::close(pub_conn)
mqtt5::unsubscribe(sub_conn)
```
