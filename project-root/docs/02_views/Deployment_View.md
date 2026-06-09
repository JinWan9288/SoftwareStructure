# Deployment_View

## 1. 视图说明

- **视图编号**: View-009
- **视图类型**: C4 Deployment View
- **目标**: 从云原生视角说明生产环境部署拓扑、Region/AZ、网络分区、负载均衡、存储层和高可用策略。

## 2. 生产环境部署拓扑图

```mermaid
flowchart TB
    student["Person: 学生"]
    teacher["Person: 教师"]
    pay["External: 第三方支付平台"]
    video["External: 第三方视频云"]
    cdn["External: 第三方 CDN 边缘节点"]
    monitor["External: 监控/告警平台"]

    subgraph region["Cloud Region: cn-east"]
        subgraph public["Public Subnet 公网入口区"]
            lb["Layer 7 Load Balancer<br/>HTTPS/WSS 入口，跨 AZ 分发"]
            waf["WAF + DDoS Protection<br/>攻击防护、黑白名单、基础限流"]
        end

        subgraph azA["Availability Zone A - Application Subnet"]
            apiA["API Gateway x2"]
            courseA["Course Service x2"]
            orderA["Order Service x2"]
            liveA["Live Access Service x3"]
            barrageA["Barrage Service x3"]
            workerA["Transcode Worker x2"]
        end

        subgraph azB["Availability Zone B - Application Subnet"]
            apiB["API Gateway x2"]
            entitlementB["Entitlement Service x2"]
            mediaB["Media Auth Service x2"]
            learningB["Learning Record Service x2"]
            barrageB["Barrage Service x3"]
            workerB["Transcode Worker x2"]
        end

        subgraph data["Private Data Subnet 私有数据区"]
            mysql[("MySQL Cluster<br/>业务主库/从库")]
            redis[("Redis Cluster<br/>缓存、限流、互动状态")]
            mq[("Message Queue Cluster<br/>支付、学习进度、转码事件")]
            oss[("Object Storage<br/>录播文件、HLS 切片")]
        end

        subgraph observe["Observability Subnet 可观测性区"]
            otel["OpenTelemetry Collector x2"]
            logStore["Log/Metric Store<br/>Prometheus/Loki/ELK"]
        end
    end

    student -->|"HTTPS/WSS 业务 API 和弹幕"| lb
    student -->|"HTTP-FLV/HLS 拉流"| cdn
    teacher -->|"HTTPS 课程管理和开播控制"| lb
    teacher -->|"RTMP/WebRTC 推流"| video
    pay -->|"HTTPS Webhook"| lb

    lb -->|"HTTPS"| waf
    waf -->|"跨 AZ 转发"| apiA
    waf -->|"跨 AZ 转发"| apiB

    apiA -->|"REST"| courseA
    apiA -->|"REST"| orderA
    apiA -->|"REST"| liveA
    apiB -->|"REST"| entitlementB
    apiB -->|"REST"| mediaB
    apiB -->|"REST"| learningB
    apiA -->|"WebSocket Upgrade"| barrageA
    apiB -->|"WebSocket Upgrade"| barrageB

    liveA -->|"Redis 权益缓存/限流"| redis
    liveA -->|"SQL 回源"| mysql
    liveA -->|"HTTPS API 受熔断保护"| video
    courseA -->|"Redis 热点缓存"| redis
    courseA -->|"SQL 查询"| mysql
    orderA -->|"SQL 订单写入"| mysql
    orderA -->|"MQ OrderPaidEvent"| mq
    mq -->|"MQ OrderPaidEvent"| entitlementB
    entitlementB -->|"SQL 权益写入"| mysql
    entitlementB -->|"Redis 权益缓存刷新"| redis
    mediaB -->|"Signed URL"| cdn
    learningB -->|"MQ LearningProgressEvent"| mq
    barrageA -->|"Redis 房间状态"| redis
    barrageB -->|"Redis 房间状态"| redis
    workerA -->|"S3 API 上传切片"| oss
    workerB -->|"S3 API 上传切片"| oss
    cdn -->|"HTTPS 点播回源"| oss

    apiA -->|"OTLP"| otel
    apiB -->|"OTLP"| otel
    liveA -->|"OTLP"| otel
    orderA -->|"OTLP"| otel
    barrageA -->|"OTLP"| otel
    learningB -->|"OTLP"| otel
    otel -->|"写入指标日志"| logStore
    otel -->|"告警和 Trace 转发"| monitor

    classDef node fill:#d9eaf7,stroke:#2f75b5,color:#111;
    classDef datastore fill:#e2f0d9,stroke:#548235,color:#111;
    classDef external fill:#eeeeee,stroke:#666,color:#111;
    class lb,waf,apiA,courseA,orderA,liveA,barrageA,workerA,apiB,entitlementB,mediaB,learningB,barrageB,workerB,otel,logStore node;
    class mysql,redis,mq,oss datastore;
    class pay,video,cdn,monitor external;
```

## 3. 网络分区

| 分区 | 部署内容 | 访问控制 |
|---|---|---|
| Public Subnet | Load Balancer、WAF、DDoS Protection | 对公网开放 HTTPS/WSS，只转发到 API Gateway |
| Application Subnet | API Gateway、业务服务、弹幕服务、Worker | 不直接暴露公网；允许服务间白名单通信和必要外部 API 出站 |
| Private Data Subnet | MySQL、Redis、MQ、Object Storage 私有访问入口 | 不对公网开放，只允许应用子网访问 |
| Observability Subnet | OTel Collector、日志指标存储 | 接收应用遥测，运维通过受控入口访问 |

## 4. 高可用策略

| 策略 | 说明 | 对应质量属性 |
|---|---|---|
| 跨 AZ 多副本部署 | API Gateway、Live Access、Barrage、Learning 等服务至少跨两个可用区部署 | 可用性、可伸缩性 |
| 负载均衡健康检查 | LB 只将流量转发到健康实例，异常实例自动摘除 | 可用性 |
| CDN 边缘分发 | 学生拉流直接访问 CDN，中心系统只负责签名和鉴权 | 性能、可伸缩性 |
| MySQL 主从 | 主库承载写入，从库承接低优先级查询和报表 | 性能、可用性 |
| Redis/MQ 集群 | 缓存、限流、异步事件具备集群冗余 | 可用性 |
| 熔断降级 | 第三方视频云异常时 Live Access 快速失败或返回排队提示 | 可用性 |
| 滚动发布 | 互动服务等模块通过 rolling update 发布 | 可修改性 |
| TraceID 全链路追踪 | API 和 MQ 事件统一透传 TraceID | 可观测性 |

## 5. 降级策略

- 视频云 API 抖动时，Live Access Service 返回 429 或“正在排队中”，不阻塞已在直播间内的拉流用户。
- Barrage Service 异常时，前端降级为“可观看、不可互动”，视频播放主链路继续可用。
- Redis 故障时，Course Service 和 Live Access Service 限流回源，避免数据库被瞬时打满。
- MQ 积压时，支付权益和学习进度进入最终一致窗口，通过消费者恢复和对账任务补偿。
