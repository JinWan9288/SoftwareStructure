# View_Consistency_Check

## 1. 检查说明

- **目标**: 对所有视图进行一致性核查，确认需求、ADR、容器、组件、动态流程和部署拓扑之间没有明显矛盾。
- **检查范围**: Context_View、Container_View、Component_View、Dynamic_Views、Deployment_View。
- **检查方式**: 使用矩阵逐项核对视图间实体、关系、协议、质量属性和 ADR 追溯。

## 2. 视图一致性检查矩阵

| 检查项 | 视图A | 视图B | 是否一致 | 说明 |
|---|---|---|---|---|
| 外部系统边界 | Context View | Container View | 是 | 第三方视频云、CDN、支付平台、监控平台均作为外部系统，不纳入平台内部实现。 |
| 用户角色 | Context View | Container View | 是 | 学生、教师、管理员/运营均在上下文图中出现，并通过前端或平台入口访问系统。 |
| 学生拉流路径 | Context View | Deployment View | 是 | 学生直接访问 CDN 拉取 HTTP-FLV/HLS，中心平台只负责鉴权和签名。 |
| 教师推流路径 | Context View | Deployment View | 是 | 教师通过 RTMP/WebRTC 推流到第三方视频云，平台负责课程和开播控制。 |
| 直播进入链路 | Container View | Component View | 是 | Container View 中的 Live Access Service 在组件图中展开为限流、缓存、熔断、Token 签发等组件。 |
| 直播进入主流程 | Component View | Dynamic View-005 | 是 | 动态视图中的 L1/L2 缓存、DB 回源、视频云调用和 Token 签发均可映射到 Live Access 组件图。 |
| 视频云熔断 | Component View | Dynamic View-007 | 是 | 两者均描述 CircuitBreaker 保护视频云 API，异常时快速失败或排队。 |
| 支付权益链路 | Container View | Component View | 是 | Order Service、Entitlement Service、MQ、Order DB、Entitlement DB 在两个视图中一致。 |
| 支付幂等处理 | Component View | Dynamic View-006 | 是 | 两者均使用 `paymentOrderId` 做订单侧幂等，使用 `userId + courseId` 做权益侧二次幂等。 |
| 点播防盗链 | Context View | Container View | 是 | Media Auth Service 生成短期签名 URL，CDN 边缘节点执行防盗链校验。 |
| 课程高频浏览 | QAS 清单 | Container View | 是 | Container View 展示 Course Service 与 Redis 热点缓存；原文档未单独新增 ADR。 |
| 互动功能热更新 | QAS 清单 | Deployment View | 是 | Barrage Service 独立部署并跨 AZ 多副本；原文档未单独新增 ADR。 |
| 学习进度异步化 | Container View | Dynamic View-008 | 是 | Learning Record Service 写入 MQ 后快速返回，Worker 聚合批量落库；原文档未单独新增 ADR。 |
| 转码异步任务 | Container View | Deployment View | 是 | Transcode Worker、MQ、Object Storage 在容器图和部署图中一致。 |
| 数据隔离 | Container View | ADR-005 | 是 | MySQL 业务表通过 `campus_id` 做逻辑隔离。 |
| 可观测性链路 | Context View | Deployment View | 是 | 所有服务通过 OpenTelemetry Collector 上报到监控/告警平台。 |

## 3. QAS 到视图追溯矩阵

| QAS编号 | 质量场景 | 相关ADR | 相关视图 | 覆盖方式 |
|---|---|---|---|---|
| QAS-001 | 进入直播间洪峰 | ADR-002a、ADR-003 | View-002、View-003、View-005、View-009 | 缓存、限流、CDN 卸载、跨 AZ 部署。 |
| QAS-002 | 课程详情高频浏览 | 无 | View-002、View-009 | Course Service、Redis 热点缓存、数据库读压力隔离。 |
| QAS-003 | 视频云接口抖动 | ADR-002a | View-003、View-007、View-009 | 200ms 超时、熔断、快速失败、降级提示。 |
| QAS-004 | 支付回调重复与延迟 | ADR-001a | View-002、View-004、View-006 | 订单幂等、MQ 异步发放、权益二次幂等、对账补偿。 |
| QAS-005 | 点播资源防盗用 | ADR-006 | View-001、View-002、View-003 | 短期播放令牌、签名 URL、CDN 边缘校验。 |
| QAS-006 | 线上系统故障定位 | ADR-001a、ADR-002a | View-001、View-002、View-003、View-009 | TraceID 透传、OTel Collector、日志指标告警。 |
| QAS-007 | 交互功能热更新 | 无 | View-002、View-009 | Barrage Service 独立容器、多副本部署、滚动发布。 |
| QAS-008 | 异步学习进度大吞吐量 | 无 | View-002、View-008、View-009 | MQ 削峰、窗口聚合、批量落库、Worker 水平扩展。 |

## 4. ADR 到视图追溯矩阵

| ADR编号 | 决策标题 | 相关视图 | 说明 |
|---|---|---|---|
| ADR-001a | 支付核心链路采用异步事件驱动、最终一致与对账补偿 | View-002、View-004、View-006、View-009 | 视图展示 Order Service、MQ、Entitlement Service、幂等和对账任务。 |
| ADR-002a | 进入直播间采用权益缓存、短期播放令牌、限流与熔断 | View-002、View-003、View-005、View-007、View-009 | 视图展示 L1/L2 缓存、熔断器、PlayToken 和降级语义。 |
| ADR-003 | 源站集群调度与第三方 CDN 边缘节点分发 | View-001、View-002、View-005、View-009 | 视图展示学生拉流直接访问 CDN，中心平台不承载出口流量。 |
| ADR-004 | 视频转码服务采用消息队列驱动的异步任务 | View-002、View-009 | 视图展示 Transcode Worker、MQ 和 Object Storage。 |
| ADR-005 | 多校区数据安全采用 campus_id 逻辑隔离 | View-002 | 容器图明确 MySQL 业务数据带 `campus_id` 隔离约束。 |
| ADR-006 | 付费课程资源采用时间戳防盗链与短期动态 Token 鉴权 | View-001、View-002、View-003 | 视图展示 Media Auth Service、PlayTokenIssuer 和 CDN 校验。 |

## 5. 结论

​		综合以上一致性检查，系统上下文图、容器图、组件图、动态视图和部署视图在系统边界、用户角色、外部系统、核心容器、组件职责、通信协议、部署节点和质量属性追溯方面保持一致。各视图均围绕核心业务链路展开，没有发现同一对象在不同视图中命名冲突、职责冲突或依赖方向冲突的问题。

​		从质量属性覆盖情况看，QAS-001、QAS-003、QAS-004、QAS-005、QAS-006 均可追溯到已有 ADR，并在对应的容器图、组件图、动态视图或部署图中得到体现。QAS-002、QAS-007、QAS-008 在原始 ADR 集中没有单独决策记录，因此本阶段不额外新增 ADR，而是通过已有架构视图说明其设计落实方式：课程详情高频浏览由 Course Service 与 Redis 缓存承担，交互功能热更新由 Barrage Service 独立部署与滚动发布承担，学习进度大吞吐量由 MQ、聚合 Worker 和批量落库承担。

​		从架构决策追溯情况看，ADR-001a 至 ADR-006 均能映射到至少一个 Phase 2 视图。其中支付异步一致性、直播间接入保护、CDN 分发、异步转码、校区数据隔离和防盗链鉴权等关键决策，已经分别在容器、组件、动态或部署视图中形成可检查的结构化表达。

​		因此，本阶段视图集合满足 对于C4 视图、关键动态场景、云原生部署拓扑和一致性核查的要求。后续若新增质量场景或新增 ADR，应同步更新本文件中的 QAS 到视图追溯矩阵、ADR 到视图追溯矩阵以及 ADR_Index.md 中的视图索引，避免追溯链断裂。
