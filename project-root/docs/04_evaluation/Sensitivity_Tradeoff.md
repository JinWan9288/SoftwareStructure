# Sensitivity_Tradeoff

## 1. 分析说明

本文件对 Phase 3 架构评估中识别出的敏感点和权衡点进行集中说明。
敏感点是指某个设计参数、组件或配置一旦变化，会显著影响一个或多个质量属性的架构要素；权衡点是指同一设计同时改善某些质量属性、削弱另一些质量属性的架构取舍。

分析依据包括：

- `docs/01_adf/ADF_Brief.md`
- `docs/01_adf/Quality_Scenarios.md`
- `docs/02_views/Context_View.md`
- `docs/02_views/Container_View.md`
- `docs/02_views/Component_View.md`
- `docs/02_views/Dynamic_Views.md`
- `docs/02_views/Deployment_View.md`
- `docs/03_adrs/ADR_Index.md`
- `docs/03_adrs/ADR-001a_Payment_Callback.md`
- `docs/03_adrs/ADR-002a_Live_Access.md`
- `docs/03_adrs/ADR-003_Deployment_Strategy.md`
- `docs/03_adrs/ADR-004_Async_Transcoding.md`
- `docs/03_adrs/ADR-005_Multi_Campus_Isolation.md`
- `docs/03_adrs/ADR-006_Anti_Leech_Protection.md`

## 2. 敏感点清单

| ID | 描述 | 影响的质量属性 | 涉及组件 |
|---|---|---|---|
| SP-001 | Live Access 的 L1/L2 权益缓存 TTL 与命中率直接影响入口延迟、数据库压力和退款后的短期一致性窗口。 | 性能、可用性、一致性 | Live Access Service、Caffeine、Redis、MySQL |
| SP-002 | 入口限流阈值和排队策略决定高峰期是保护系统还是过早拒绝用户。 | 性能、可用性、用户体验 | API Gateway、AdmissionRateLimiter、Redis |
| SP-003 | 视频云 API 的 200ms 超时阈值、20% 错误率阈值、60s 熔断窗口决定外部依赖异常时的隔离效果。 | 可用性、性能 | CircuitBreaker、VideoCloudClient、第三方视频云 |
| SP-004 | PlayToken 的 5 分钟 TTL、IP/User-Agent 绑定和签名算法影响盗链拦截率与合法用户播放成功率。 | 安全性、可用性 | PlayTokenIssuer、Media Auth Service、CDN |
| SP-005 | CDN 回源策略、节点健康和边缘防盗链配置决定大规模播放体验与资源安全。 | 性能、可用性、安全性 | 第三方 CDN、Object Storage、Media Auth Service |
| SP-006 | 支付回调 `paymentOrderId` 唯一约束和订单状态机单向流转规则决定重复回调是否安全。 | 一致性、可用性 | Order Service、Order DB |
| SP-007 | 权益侧 `userId + courseId` 二次幂等约束决定重复事件消费是否会重复发放课程权益。 | 一致性 | Entitlement Service、Entitlement DB |
| SP-008 | MQ 的持久化、重试、死信队列和消费 Lag 告警决定支付权益、学习进度、转码任务的最终一致窗口。 | 可用性、一致性、性能 | Message Queue、Entitlement Service、Learning Worker、Transcode Worker |
| SP-009 | Learning Worker 的窗口聚合大小和批量 UPSERT 频率决定数据库写压力与学习进度延迟。 | 性能、一致性 | Learning Record Service、Progress Aggregation Worker、MySQL |
| SP-010 | `campus_id` 逻辑隔离拦截器覆盖范围决定跨校区越权风险。 | 安全性、可维护性 | DAO、MySQL、API Gateway |
| SP-011 | OpenTelemetry TraceID 是否贯穿同步 REST 与异步 MQ 链路决定故障定位效率。 | 可观测性、可维护性 | API Gateway、Order Service、Live Access Service、MQ、OTel Collector |
| SP-012 | Barrage Service 的滚动发布摘流和 WebSocket 重连策略决定互动功能热更新对在线课堂的影响。 | 可修改性、可用性 | Barrage Service、Load Balancer、Frontend |

## 3. 敏感点分析

### SP-001：权益缓存 TTL 与命中率

缓存 TTL 太短会增加 Redis 和 MySQL 回源压力，降低 QAS-001 的性能保障；TTL 太长会扩大退款或权限变更后的短期越权窗口。当前 ADR-002a 使用 Redis TTL=60s，是性能和一致性之间的折中。建议在压测中重点观察缓存命中率、MySQL QPS、P95 延迟和缓存失效瞬间的回源峰值。

### SP-003：视频云熔断参数

熔断阈值过低会导致第三方视频云短暂抖动时系统过早进入降级；阈值过高会导致应用线程池被慢调用拖垮。当前设计采用 200ms 超时、错误率或超时率达到 20% 后熔断 60s，符合 QAS-003 对 30s 内完成断路器全开的要求，但仍需要结合真实视频云 SLA 调整。

### SP-004：Token TTL、绑定条件与时钟同步

Token TTL 越短，盗链窗口越小，但合法用户在网络较差或时钟漂移时越容易遇到 403；TTL 越长，播放成功率提高，但被截获后的可利用时间也变长。当前 5 分钟 TTL 适合作为课程项目设计，但必须依赖 NTP 时间同步和密钥轮换流程。

### SP-008：MQ 可靠性与消费 Lag

MQ 是支付权益、学习进度和转码任务的共同基础设施。它提高了削峰和解耦能力，但也使最终一致性依赖消息持久化、重试、死信队列和消费组扩容。若 MQ Lag 未被监控，风险会从同步阻塞转移为后台积压。

### SP-010：多校区逻辑隔离拦截器

`campus_id` 逻辑隔离降低成本，但安全性高度依赖 DAO 拦截器是否覆盖所有查询、更新和删除路径。原生 SQL、批处理任务、报表查询和管理员接口都可能成为绕过点，因此需要自动化越权测试与 SQL 审计。

## 4. 权衡点清单

| ID | 描述 | 正向影响 | 负向影响 |
|---|---|---|---|
| TP-001 | 使用 L1/L2 缓存保护直播入口权益查询。 | 提升 QAS-001 性能，降低 MySQL 压力，支撑高峰进入直播间。 | 权益变化存在短期不一致窗口，缓存失效时可能产生回源峰值。 |
| TP-002 | 使用限流和排队语义保护入口服务。 | 防止洪峰拖垮核心服务，保障系统整体可用性。 | 部分学生会收到排队或 429，短期用户体验下降。 |
| TP-003 | 使用熔断器隔离第三方视频云。 | 避免慢调用耗尽线程池，满足 QAS-003 的防雪崩目标。 | 视频云短暂异常时可能过早拒绝新进入直播间请求。 |
| TP-004 | 使用 MQ 异步发放支付权益。 | 支付回调快速返回，隔离订单和权益服务，提升可用性。 | 从强一致变为最终一致，用户可能短暂看不到已购课程。 |
| TP-005 | 使用第三方 CDN 分发直播/点播流。 | 卸载中心带宽，提升跨地域播放性能。 | 引入外部强依赖，防盗链和节点健康配置复杂度增加。 |
| TP-006 | 使用短期动态 Token 防盗链而非 DRM。 | 性能成本低，CDN 边缘可 O(1) 校验，工程复杂度可控。 | 不能防录屏，依赖密钥管理、IP 绑定和时间同步。 |
| TP-007 | 使用 `campus_id` 共享库表逻辑隔离。 | 降低多校区部署成本，便于统一升级和维护。 | 物理隔离弱，存在嘈杂邻居和拦截器漏配风险。 |
| TP-008 | 学习进度采用 MQ + 窗口聚合 + 批量落库。 | 降低高频写数据库压力，API 可快速返回。 | 学习进度存在小于 30 秒的最终一致延迟。 |
| TP-009 | Barrage Service 独立部署并滚动发布。 | 互动功能可独立演进，降低对直播主链路侵入。 | WebSocket 长连接发布期间需要额外连接管理。 |
| TP-010 | 转码采用异步 Worker。 | 转码不阻塞 Web 主链路，任务可重试可削峰。 | 视频上传后不能立即播放，需要转码状态反馈。 |

## 5. 权衡点结论

当前架构的主要取舍方向是：用缓存、CDN 和异步消息提升性能与可用性，同时接受有限的最终一致性窗口和外部依赖复杂度。对在线教育直播与点播平台而言，这一取舍与业务驱动因素基本匹配，因为直播观看体验、交易可靠性和付费内容安全优先于严格同步一致和完全自研基础设施。

后续评估和实现中应优先关注 TP-001、TP-003、TP-004、TP-005 和 TP-006，因为它们直接影响 Must Have 级别的性能、可用性和安全性目标。

