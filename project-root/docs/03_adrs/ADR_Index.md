## ADR_Index（ADR索引表）

---

> **起始日期:** 2025-11-10
> *注：本索引表完整记录了系统从“初期单体/同步架构”向“高并发/异步架构”演进的决策轨迹。标记为 `Deprecated` 的决策为早期方案，由于无法满足激增的并发需求已被废弃并替代。*

| ADR编号      | 标题                                                         | 状态           | 关联QAS              | 关联容器/组件          | 最近更新   |
| :----------- | :----------------------------------------------------------- | :------------- | :------------------- | :--------------------- | :--------- |
| ADR-001      | 支付回调采用“同步 RPC 强一致调用”                            | **Deprecated** | -                    | 订单服务, 权益服务     | 2025-11-10 |
| **ADR-001a** | **支付核心链路采用“异步事件驱动、最终一致与对账补偿”** *(替换 ADR-001)* | **Accepted**   | QAS-004              | 订单服务, 权益服务, MQ | 2026-05-28 |
| ADR-002      | 进入直播间采用“直连数据库与视频云同步校验”                   | **Deprecated** | -                    | 直播接入服务           | 2025-11-12 |
| **ADR-002a** | **进入直播间采用“权益缓存+短期播放令牌+分级限流与熔断”** *(替换ADR-002)* | **Accepted**   | QAS-001, QAS-003     | 直播接入服务，缓存集群 | 2026-05-28 |
| ADR-003      | 部署策略采用“源站集群调度与第三方 CDN 边缘分发”              | Accepted       | QAS-001              | 源站集群, CDN 边缘节点 | 2026-05-28 |
| ADR-004      | 视频转码服务采用“消息队列驱动的异步任务”架构                 | Accepted       | 补充点播转码链路场景 | 转码 Worker, OSS       | 2026-05-28 |
| ADR-005      | 多校区数据安全采用“逻辑隔离（campus_id 共享表）”架构         | Accepted       | 多校区数据隔离场景   | 核心数据访问层 (DAO)   | 2026-05-28 |
| ADR-006      | 付费课程资源采用“时间戳防盗链与短期动态 Token 鉴权”          | Proposed       | QAS-005              | 鉴权网关, 媒体服务     | 2026-06-03 |

---

## Views Index (视图目录索引表)

*注：本视图集合严格遵循 C4 模型标准与 UML 规范，用于对核心架构决策进行可视化映射与验证。视图编号、文件名、视图类型与 `docs/02_views/` 中的实际内容保持一致。*

| 视图编号 | 所在文件                           | 视图名称                                  | 视图类型                    | 关联ADR/QAS                                                  | 关联组件/外部系统                                            |
| :------- | :--------------------------------- | :---------------------------------------- | :-------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| View-001 | `docs/02_views/Context_View.md`    | 在线教育平台全局系统上下文图              | C4 Level 1 - System Context | ADR-003, ADR-006; QAS-001, QAS-004, QAS-005, QAS-006         | 学生、教师、管理员、支付平台、视频云、CDN、监控平台          |
| View-002 | `docs/02_views/Container_View.md`  | 核心业务微服务与中间件容器图              | C4 Level 2 - Container      | ADR-001a, ADR-002a, ADR-003, ADR-004, ADR-005, ADR-006; QAS-001 至 QAS-008 | API Gateway、Course、Order、Entitlement、Live Access、Media Auth、Barrage、Learning、Transcode、MySQL、Redis、MQ、OSS |
| View-003 | `docs/02_views/Component_View.md`  | 直播接入服务 (Live Access Service) 组件图 | C4 Level 3 - Component      | ADR-002a, ADR-006; QAS-001, QAS-003, QAS-005                 | LiveAccessController、EntitlementChecker、CircuitBreaker、PlayTokenIssuer |
| View-004 | `docs/02_views/Component_View.md`  | 支付回调与权益发放组件图                  | C4 Level 3 - Component      | ADR-001a; QAS-004                                            | PaymentCallbackController、OrderStateMachine、OrderPaidEventPublisher、OrderPaidEventConsumer、EntitlementGrantService |
| View-005 | `docs/02_views/Dynamic_Views.md`   | 进入直播间正常主流程时序图                | Dynamic View - Sequence     | ADR-002a, ADR-003, ADR-006; QAS-001, QAS-003, QAS-005        | API Gateway、Live Access Service、Redis、MySQL、视频云、CDN  |
| View-006 | `docs/02_views/Dynamic_Views.md`   | 支付成功回调与权益异步发放时序图          | Dynamic View - Sequence     | ADR-001a; QAS-004                                            | Order Service、Message Queue、Entitlement Service、Order DB、Entitlement DB |
| View-007 | `docs/02_views/Dynamic_Views.md`   | 视频云接口抖动熔断降级时序图              | Dynamic View - Sequence     | ADR-002a; QAS-003                                            | Live Access Service、CircuitBreaker、第三方视频云、Observability |
| View-008 | `docs/02_views/Dynamic_Views.md`   | 学习进度上报异步削峰时序图                | Dynamic View - Sequence     | QAS-008                                                      | Learning Record Service、Message Queue、Progress Aggregation Worker、MySQL |
| View-009 | `docs/02_views/Deployment_View.md` | 生产环境云原生部署拓扑图                  | C4 Deployment View          | ADR-002a, ADR-003, ADR-004; QAS-001, QAS-003, QAS-006, QAS-007, QAS-008 | Region、Availability Zone、Public/Application/Data/Observability Subnet、LB、WAF、MySQL、Redis、MQ、OSS |
