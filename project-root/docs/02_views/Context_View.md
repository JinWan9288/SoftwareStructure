# Context_View

## 1. 视图说明

- **视图编号**: View-001
- **C4 层级**: C4 Level 1 - System Context
- **目标**: 标明用户角色、外部系统、系统边界及交互关系。

## 2. C4 Level 1 系统上下文图

```mermaid
flowchart LR
    student["Person: 学生<br/>浏览课程、购买课程、进入直播间、观看点播、发送弹幕、上报学习进度"]
    teacher["Person: 教师<br/>配置课程大纲、开播推流、课堂控制、查看考勤和学习数据"]
    admin["Person: 管理员<br/>上架课程、配置付费权限、防盗链规则、查看订单和运营数据"]
    ops["Person: 运维人员<br/>监控在线人数、卡顿率、推拉流质量和系统告警"]

    platform["System: 在线教育直播与点播平台<br/>课程购买、订单状态机、权益管理、直播接入、点播鉴权、弹幕互动、学习数据采集"]

    pay["External System: 第三方支付平台<br/>处理实际扣款，以异步回调通知支付结果"]
    video["External System: 第三方视频云<br/>提供教师推流、直播房间、录制、转码、流媒体 API"]
    cdn["External System: 第三方 CDN<br/>边缘分发直播流和点播切片，执行防盗链校验"]
    notify["External System: 通知服务<br/>发送开课提醒、支付结果和异常提示"]
    monitor["External System: 监控/告警平台<br/>接收日志、指标、链路追踪和告警事件"]

    student -->|"HTTPS/JSON 同步: 浏览课程、下单、请求直播/点播入口"| platform
    student -->|"WebSocket/JSON 异步双向: 弹幕互动"| platform
    student -->|"HTTP-FLV/HLS 同步长连接: 拉取直播流/点播切片"| cdn

    teacher -->|"HTTPS/JSON 同步: 课程管理、开播控制、报表查看"| platform
    teacher -->|"RTMP/WebRTC 流式同步: 教师端推流"| video

    admin -->|"HTTPS/JSON 同步: 课程、权限、防盗链、订单配置"| platform
    ops -->|"Web Console 同步: 查看监控和告警"| monitor

    pay -->|"HTTPS Webhook JSON/XML 异步至少一次: 支付成功/失败回调"| platform
    platform -->|"HTTPS API/JSON 同步: 获取房间和流信息，需超时与熔断"| video
    platform -->|"签名 URL/HTTPS 同步: 下发短期播放凭证"| cdn
    platform -->|"HTTPS/MQ JSON 异步: 发送提醒和异常通知"| notify
    platform -->|"OTLP/HTTP JSON或Protobuf 异步: 上报 TraceID、指标和日志"| monitor

    classDef person fill:#fff4cc,stroke:#b8860b,color:#222;
    classDef system fill:#d9eaf7,stroke:#2f75b5,color:#111;
    classDef external fill:#eeeeee,stroke:#666,color:#111;
    class student,teacher,admin,ops person;
    class platform system;
    class pay,video,cdn,notify,monitor external;
```

## 3. 关系说明

| 关系 | 协议 | 数据格式 | 同步/异步 | 说明 |
|---|---|---|---|---|
| 学生 -> 平台 | HTTPS | JSON | 同步 | 浏览课程、下单、查询权益、请求直播或点播入口。 |
| 学生 -> 平台 | WebSocket | JSON | 异步双向 | 弹幕和互动消息，不阻塞视频播放主链路。 |
| 学生 -> CDN | HTTP-FLV/HLS | 流媒体切片/长连接 | 同步长连接 | 学生直接从 CDN 边缘节点拉流，降低中心平台出口带宽压力。 |
| 教师 -> 平台 | HTTPS | JSON | 同步 | 课程配置、开播控制、课堂管理和报表查询。 |
| 教师 -> 视频云 | RTMP/WebRTC | 流媒体 | 同步长连接 | 教师推流进入第三方视频云，平台不实现底层推流网络。 |
| 管理员 -> 平台 | HTTPS | JSON | 同步 | 配置课程权限、防盗链规则、订单和运营数据。 |
| 支付平台 -> 平台 | HTTPS Webhook | JSON/XML | 异步至少一次 | 回调可能重复或延迟，订单服务必须幂等处理。 |
| 平台 -> 视频云 | HTTPS API | JSON | 同步 | 获取直播房间、流地址和转码状态；需要超时、熔断和降级。 |
| 平台 -> CDN | Signed URL/HTTPS | URL 参数 | 同步 | 下发短期播放 URL，CDN 边缘节点校验防盗链。 |
| 平台 -> 通知服务 | HTTPS/MQ | JSON | 异步 | 非核心通知不应阻塞支付、直播和点播链路。 |
| 平台 -> 监控平台 | OTLP/HTTP | JSON/Protobuf | 异步 | 上报 TraceID、日志、指标和告警，支撑故障定位。 |

## 4. 系统边界声明

**范围内**:

- 课程购买、订单状态机、支付回调幂等。
- 课程权益管理、直播进入鉴权、点播防盗链鉴权。
- 弹幕互动、学习进度采集、异步转码任务调度。
- 缓存、消息队列、审计日志和可观测性。

**范围外**:

- 第三方支付平台的实际扣款。
- 第三方视频云的底层推流、拉流、录制和转码基础设施。
- CDN 边缘节点的物理运营和网络调度。
- 通知服务的底层短信/站内信投递通道。
